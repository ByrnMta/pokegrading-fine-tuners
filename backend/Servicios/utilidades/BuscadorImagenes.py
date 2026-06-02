import os
import io
import logging
from typing import Any, Dict, List, Optional

try:
    import numpy as np
except Exception:
    np = None

try:
    from PIL import Image
except Exception:
    Image = None

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate and search image embeddings using CLIP when available or a histogram fallback.

    Saves embeddings as .npy files in an `embeddings/` folder using the naming
    convention: {card_id}_front.npy and {card_id}_back.npy.
    """

    def __init__(self, embeddings_dir: str = "embeddings"):
        self.embeddings_dir = embeddings_dir
        os.makedirs(self.embeddings_dir, exist_ok=True)

        # Lazy CLIP availability
        self.use_clip = False
        self.clip_model = None
        self.clip_processor = None
        self.device = None
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.use_clip = True
            logger.info("EmbeddingService: CLIP loaded")
        except Exception:
            logger.info("EmbeddingService: CLIP not available, will use histogram fallback")

    def embed_image_bytes(self, image_bytes: bytes) -> Any:
        """Return a L2-normalized numpy embedding vector for the given image bytes."""
        if np is None:
            raise RuntimeError("numpy is required for embeddings")

        if self.use_clip:
            try:
                from io import BytesIO
                import torch

                img = Image.open(BytesIO(image_bytes)).convert("RGB")
                inputs = self.clip_processor(images=img, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    outputs = self.clip_model.get_image_features(**inputs)

                tensor = self._extract_embedding_tensor(outputs)
                emb = self._tensor_to_numpy(tensor)
                norm = np.linalg.norm(emb)
                if norm == 0:
                    return emb.astype("float32")
                return (emb / norm).astype("float32")
            except Exception as e:
                logger.warning(f"CLIP embedding failed, falling back: {e}")

        # Histogram fallback (KISS)
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img = img.resize((224, 224))
            arr = np.array(img)
            hists = []
            for c in range(3):
                hist, _ = np.histogram(arr[:, :, c], bins=64, range=(0, 256))
                hists.append(hist.astype("float32"))
            emb = np.concatenate(hists)
            norm = np.linalg.norm(emb)
            if norm == 0:
                return emb
            return (emb / norm).astype("float32")
        except Exception as e:
            logger.error(f"Failed to embed image bytes: {e}")
            raise

    def _extract_embedding_tensor(self, outputs: Any) -> Any:
        """Extract a tensor-like embedding from CLIP outputs."""
        if hasattr(outputs, "cpu"):
            return outputs
        if hasattr(outputs, "pooler_output") and outputs.pooler_output is not None:
            return outputs.pooler_output
        if hasattr(outputs, "image_embeds") and outputs.image_embeds is not None:
            return outputs.image_embeds
        if hasattr(outputs, "last_hidden_state") and outputs.last_hidden_state is not None:
            return outputs.last_hidden_state.mean(dim=1)
        raise RuntimeError("CLIP returned unexpected ModelOutput structure")

    def _tensor_to_numpy(self, tensor: Any) -> Any:
        """Convert a tensor-like object to a 1D numpy array."""
        if hasattr(tensor, "cpu"):
            emb = tensor.cpu().numpy()
        else:
            emb = np.asarray(tensor)
        if emb.ndim == 2 and emb.shape[0] == 1:
            emb = emb[0]
        return emb

    def persist_embeddings(self, card_id: str, front_emb: Any, back_emb: Optional[Any]) -> None:
        """Persist front/back embeddings as .npy files in the embeddings directory."""
        try:
            front_path = os.path.join(self.embeddings_dir, f"{card_id}_front.npy")
            back_path = os.path.join(self.embeddings_dir, f"{card_id}_back.npy")
            import numpy as _np

            _np.save(front_path, front_emb)
            if back_emb is not None:
                _np.save(back_path, back_emb)
            logger.info(f"Persisted embeddings for {card_id}")
        except Exception as e:
            logger.error(f"Failed persisting embeddings for {card_id}: {e}")
            raise

    def search(self, query_emb: Any, embeddings_dir: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search persisted embeddings by cosine similarity and return top_k list of {card_id, score}.

        Score is cosine similarity in [-1,1]. Results are sorted descending by score.
        """
        if embeddings_dir is None:
            embeddings_dir = self.embeddings_dir
        results: Dict[str, float] = {}
        try:
            import numpy as _np

            qnorm = _np.linalg.norm(query_emb)
            if qnorm == 0:
                return []
            q = query_emb / qnorm

            if not os.path.exists(embeddings_dir):
                return []

            for fname in os.listdir(embeddings_dir):
                if not fname.endswith('.npy'):
                    continue
                try:
                    parts = fname[:-4].rsplit('_', 1)
                    if len(parts) != 2:
                        continue
                    card_id, side = parts
                    emb = _np.load(os.path.join(embeddings_dir, fname))
                    if _np.linalg.norm(emb) == 0:
                        continue
                    emb = emb / _np.linalg.norm(emb)
                    sim = float(_np.dot(q, emb))
                    # keep max of front/back
                    if card_id not in results or sim > results[card_id]:
                        results[card_id] = sim
                except Exception as e:
                    logger.debug(f"Skipping embedding file {fname}: {e}")
                    continue

            ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)[:top_k]
            return [{"card_id": cid, "score": score} for cid, score in ranked]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def evaluate_candidates(self, candidates: List[Dict[str, Any]], threshold: float = 0.85) -> Dict[str, Any]:
        """Return decision {'decision','top'} based on threshold applied to top candidate score."""
        if not candidates:
            return {"decision": "UNLIKELY", "top": None}
        top = candidates[0]
        # scores in [-1,1] -> map to [0,1]
        top_score = (top["score"] + 1) / 2
        if top_score >= threshold:
            decision = "MATCH"
        elif top_score >= threshold * 0.75:
            decision = "POSSIBLE"
        else:
            decision = "UNLIKELY"
        return {"decision": decision, "top": top}

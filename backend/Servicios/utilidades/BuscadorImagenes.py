import os
import io
import logging
import os
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
    """Generate and search image embeddings.

    Layout on disk:
    Datos/catalogo/{card_id}/images
    Datos/catalogo/{card_id}/embeds
    """

    def __init__(self, catalogo_dir: str = os.path.join("Datos", "catalogo")):
        self.catalogo_dir = catalogo_dir
        os.makedirs(self.catalogo_dir, exist_ok=True)

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

    def create_card_directory(self, card_id: str) -> str:
        """Create Datos/catalogo/{card_id}/images and /embeds and return the card directory."""
        card_dir = os.path.join(self.catalogo_dir, card_id)
        os.makedirs(os.path.join(card_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(card_dir, "embeds"), exist_ok=True)
        return card_dir

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
        if hasattr(tensor, "cpu"):
            emb = tensor.cpu().numpy()
        else:
            emb = np.asarray(tensor)
        if emb.ndim == 2 and emb.shape[0] == 1:
            emb = emb[0]
        return emb

    def persist_embeddings(
        self,
        card_id: str,
        front_emb: Any,
        back_emb: Optional[Any],
        card_dir: Optional[str] = None,
    ) -> None:
        """Persist front/back embeddings as .npy files inside Datos/catalogo/card_id/embeds."""
        try:
            card_dir = card_dir or os.path.join(self.catalogo_dir, card_id)
            embeds_dir = os.path.join(card_dir, "embeds")
            os.makedirs(embeds_dir, exist_ok=True)

            front_path = os.path.join(embeds_dir, f"front.npy")
            back_path = os.path.join(embeds_dir, f"back.npy")

            np.save(front_path, front_emb)
            if back_emb is not None:
                np.save(back_path, back_emb)

            logger.info(f"Persisted embeddings for {card_id}")
        except Exception as e:
            logger.error(f"Failed persisting embeddings for {card_id}: {e}")
            raise

    def search(self, query_emb: Any, catalogo_dir: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search persisted embeddings by cosine similarity and return top_k list of {card_id, score}."""
        if catalogo_dir is None:
            catalogo_dir = self.catalogo_dir

        results: Dict[str, float] = {}
        try:
            qnorm = np.linalg.norm(query_emb)
            if qnorm == 0:
                return []
            q = query_emb / qnorm

            if not os.path.exists(catalogo_dir):
                return []

            for card_folder in os.listdir(catalogo_dir):
                card_dir = os.path.join(catalogo_dir, card_folder)
                embeds_dir = os.path.join(card_dir, "embeds")
                if not os.path.isdir(embeds_dir):
                    continue

                for fname in os.listdir(embeds_dir):
                    if not fname.endswith(".npy"):
                        continue
                    try:
                        emb = np.load(os.path.join(embeds_dir, fname))
                        if np.linalg.norm(emb) == 0:
                            continue
                        emb = emb / np.linalg.norm(emb)
                        sim = float(np.dot(q, emb))
                        if card_folder not in results or sim > results[card_folder]:
                            results[card_folder] = sim
                    except Exception as e:
                        logger.debug(f"Skipping embedding file {fname}: {e}")
                        continue

            ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)[:top_k]
            return [{"card_id": cid, "score": score} for cid, score in ranked]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def evaluate_candidates(self, candidates: List[Dict[str, Any]], threshold: float = 0.85) -> Dict[str, Any]:
        if not candidates:
            return {"decision": "UNLIKELY", "top": None}

        top = candidates[0]
        top_score = (top["score"] + 1) / 2
        if top_score >= threshold:
            decision = "MATCH"
        elif top_score >= threshold * 0.75:
            decision = "POSSIBLE"
        else:
            decision = "UNLIKELY"
        return {"decision": decision, "top": top}

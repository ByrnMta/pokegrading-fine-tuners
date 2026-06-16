import io
import logging
from typing import Any

try:
    import numpy as np
except Exception:
    np = None

try:
    from PIL import Image
except Exception:
    Image = None

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Genera embeddings para imágenes usando CLIP o histograma como fallback."""

    def __init__(self):
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
            logger.info("EmbeddingGenerator: CLIP cargado")
        except Exception:
            logger.info("EmbeddingGenerator: CLIP no disponible, se usará histograma como fallback")

    def embed_image_bytes(self, image_bytes: bytes) -> Any:
        """Retorna un vector de embedding numpy L2-normalizado para los bytes de imagen dados."""
        if np is None:
            raise RuntimeError("numpy es requerido para embeddings")

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
                logger.warning(f"Embedding con CLIP falló, usando fallback: {e}")

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
            logger.error(f"Fallo al generar embedding para imagen: {e}")
            raise

    def _extract_embedding_tensor(self, outputs: Any) -> Any:
        """Extrae el tensor de embedding de la salida del modelo CLIP."""
        if hasattr(outputs, "cpu"):
            return outputs
        if hasattr(outputs, "pooler_output") and outputs.pooler_output is not None:
            return outputs.pooler_output
        if hasattr(outputs, "image_embeds") and outputs.image_embeds is not None:
            return outputs.image_embeds
        if hasattr(outputs, "last_hidden_state") and outputs.last_hidden_state is not None:
            return outputs.last_hidden_state.mean(dim=1)
        raise RuntimeError("CLIP retornó una estructura ModelOutput inesperada")

    def _tensor_to_numpy(self, tensor: Any) -> Any:
        """Convierte un tensor de PyTorch a numpy array."""
        if hasattr(tensor, "cpu"):
            emb = tensor.cpu().numpy()
        else:
            emb = np.asarray(tensor)
        if emb.ndim == 2 and emb.shape[0] == 1:
            emb = emb[0]
        return emb
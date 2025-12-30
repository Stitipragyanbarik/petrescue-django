import os
import numpy as np

def _get_tf_model():
    try:
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        from tensorflow.keras.preprocessing import image as keras_image
    except Exception:
        return None

    base = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

    def img_to_embedding(path):
        img = keras_image.load_img(path, target_size=(224, 224))
        x = keras_image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        emb = base.predict(x)
        return emb.flatten()

    return img_to_embedding


def compute_embedding_for_image(path):
    """Return embedding vector for image path, or None if TF not available."""
    fn = _get_tf_model()
    if fn is None:
        return None
    try:
        return fn(path)
    except Exception:
        return None


def build_embeddings(output_dir, pet_qs):
    """Compute and save embeddings for queryset of Pet objects.

    `output_dir` will be created if missing. Embeddings are saved as
    `pet_{id}.npy`.
    Returns number of embeddings written.
    """
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for pet in pet_qs:
        if not pet.image:
            continue
        path = pet.image.path
        emb = compute_embedding_for_image(path)
        if emb is None:
            continue
        out = os.path.join(output_dir, f'pet_{pet.id}.npy')
        np.save(out, emb.astype(np.float32))
        count += 1
    return count


def find_similar_embeddings(query_path, embeddings_dir, top_k=10):
    """Compute embedding for `query_path` and return list of (score, filename)
    sorted by descending cosine similarity. Returns [] if TF not available or
    embeddings_dir empty.
    """
    query = compute_embedding_for_image(query_path)
    if query is None:
        return []
    files = [f for f in os.listdir(embeddings_dir) if f.endswith('.npy')]
    if not files:
        return []
    mats = []
    for f in files:
        try:
            v = np.load(os.path.join(embeddings_dir, f))
            mats.append((f, v))
        except Exception:
            continue
    if not mats:
        return []

    # compute cosine similarity
    q = query / np.linalg.norm(query)
    scored = []
    for fname, v in mats:
        if np.linalg.norm(v) == 0:
            continue
        s = float(np.dot(q, v / np.linalg.norm(v)))
        scored.append((s, fname))
    scored.sort(reverse=True, key=lambda t: t[0])
    return scored[:top_k]

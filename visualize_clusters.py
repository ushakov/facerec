import json
from dataclasses import dataclass
import streamlit as st
import numpy as np
from pathlib import Path
import models
import images
from collections import defaultdict, Counter
import random

st.set_page_config(layout="wide")

class Embeddings:
    def __init__(self, embeddings, face_ids):
        self.embeddings = embeddings
        self.embeddings /= np.linalg.norm(self.embeddings, axis=1)[:, None]
        self.face_ids = face_ids
        self.rev_face_ids = {face_id: idx for idx, face_id in enumerate(face_ids)}

    def nearest_neighbors(self, face_id: int, n: int = 5):
        embedding = self.embeddings[self.rev_face_ids[face_id]]
        cosine_dists = 1 - np.dot(self.embeddings, embedding)
        return [self.face_ids[i] for i in cosine_dists.argsort()[:n]]

    def distance(self, face_id_0: int, face_id_1: int):
        embedding_0 = self.embeddings[self.rev_face_ids[face_id_0]]
        embedding_1 = self.embeddings[self.rev_face_ids[face_id_1]]
        return 1 - np.dot(embedding_0, embedding_1)


# Load data
@st.cache_data
def load_data():
    emb = np.load('faces.npz')
    embeddings = emb['faces']
    embeddings /= np.linalg.norm(embeddings, axis=1)[:, None]
    face_ids = emb['face_ids']
    embeddings = Embeddings(embeddings, face_ids)

    data = np.load('clustering.npz', allow_pickle=True)
    assignments = data['assignments'].item()
    cluster_sizes = data['cluster_sizes'].item()
    suspicious_pairs = data['suspicious_face_pairs']
    suspicious_pairs = [
        (face_ids[i], face_ids[j]) for i, j in suspicious_pairs
    ]

    # Create face_id -> cluster mapping
    face_clusters = {face_ids[k]: v for k, v in assignments.items()}

    # Group faces by cluster
    cluster_faces = defaultdict(list)
    for face_id, cluster in face_clusters.items():
        cluster_faces[int(cluster)].append(int(face_id))

    return face_clusters, cluster_faces, cluster_sizes, suspicious_pairs, embeddings

@dataclass
class LoadedFace:
    error: str | None
    face: models.Face | None
    image: models.Image | None
    face_img: np.ndarray | None

    def angles(self):
        if self.face is None:
            return None
        face_data = json.loads(self.face.face_data)
        return [int(x) for x in face_data['pose']]

    def age(self):
        if self.face is None:
            return None
        face_data = json.loads(self.face.face_data)
        return face_data['age']

    def year(self):
        if self.image is None:
            return None
        return self.image.capture_date.year

def get_face_image(face_id: int, Session, max_size: int = 200):
    """Load and prepare face image"""
    with Session() as session:
        face = session.query(models.Face).filter(models.Face.id == int(face_id)).first()
        if not face:
            return LoadedFace(f"cannot find face {face_id}", None, None, None)

        image = session.query(models.Image).filter(models.Image.id == face.image_id).first()
        if not image:
            return LoadedFace(f"cannot find image {face.image_id}", face, None, None)

        # img_path = Path(image.best_filename)
        # full_img = images.get_image(img_path)
        # if full_img is None:
        #     return LoadedFace(f"cannot load image {img_path}", face, image, None)

        # face_img = images.cut_face(full_img, face)
        # face_img = images.prepare_image(face_img, max_size)
        fname = Path('faces_extr') / f"face_{face.id}.jpg"
        face_img = images.get_image(fname)
        if face_img is None:
            return LoadedFace(f"cannot load image {fname}", face, image, None)
        face_img = images.prepare_image(face_img, max_size)
    return LoadedFace(None, face, image, face_img)


def format_caption(loaded_face: LoadedFace):
    return f"Face ID: {loaded_face.face.id} - {loaded_face.angles()} - {loaded_face.year()}"


def nearest_button(where, embeddings: Embeddings, face_id: int, Session):
    with where.popover('[Near]'):
        nearest = embeddings.nearest_neighbors(face_id)
        for n in nearest:
            lf = get_face_image(n, Session)
            st.image(lf.face_img)



def main():
    st.title("Face Clustering Visualization")

    face_clusters, cluster_faces, cluster_sizes, suspicious_pairs, embeddings = load_data()
    Session = models.open_session()

    # Sidebar - Cluster Selection
    sorted_clusters = sorted(cluster_sizes.items(), key=lambda x: x[1], reverse=True)
    selected_cluster = st.sidebar.selectbox(
        "Select Cluster",
        [c[0] for c in sorted_clusters],
        format_func=lambda x: f"Cluster {x} (size: {cluster_sizes[x]})"
    )

    # Main view - Selected Cluster
    st.header(f"Cluster {selected_cluster} - {cluster_sizes[selected_cluster]} faces")

    sample_size = min(9, len(cluster_faces[selected_cluster]))
    sample_faces = random.sample(cluster_faces[selected_cluster], sample_size)

    cols = st.columns(3)
    for idx, face_id in enumerate(sample_faces):
        loaded_face = get_face_image(face_id, Session)
        if loaded_face.error is None:
            cols[idx % 3].image(loaded_face.face_img, caption=format_caption(loaded_face))
            nearest_button(cols[idx % 3], embeddings, face_id, Session)
        else:
            cols[idx % 3].error(loaded_face.error)

    # Suspicious Pairs
    st.header("Suspicious Pairs")

    neighboring_clusters = defaultdict(list)
    for pair in suspicious_pairs:
        if face_clusters[pair[0]] == selected_cluster:
            neighboring_clusters[face_clusters[pair[1]]].append(pair)
        elif face_clusters[pair[1]] == selected_cluster:
            neighboring_clusters[face_clusters[pair[0]]].append(pair)

    sorted_neighboring_clusters = [
        (cluster, len(pairs)) for cluster, pairs in neighboring_clusters.items()
    ]
    sorted_neighboring_clusters.sort(key=lambda x: x[1], reverse=True)

    selected_pair = st.selectbox(
        "Select Suspicious Neighboring Cluster",
        sorted_neighboring_clusters,
        format_func=lambda p: f"Cluster {p[0]} ({p[1]} connections)"
    )

    if selected_pair:
        other_cluster = selected_pair[0]
        st.subheader(f"Cluster {other_cluster}")

        cols = st.columns(2)
        # Show sample neighboring face pairs
        sample_size = min(6, len(neighboring_clusters[other_cluster]))
        sample = random.sample(neighboring_clusters[other_cluster], sample_size)
        for cidx, pair in enumerate(sample):
            loaded_face_0 = get_face_image(pair[0], Session)
            if loaded_face_0.error is None:
                cols[0].image(loaded_face_0.face_img, caption=format_caption(loaded_face_0))
                nearest_button(cols[0], embeddings, pair[0], Session)
            else:
                cols[0].error(loaded_face_0.error)
            loaded_face_1 = get_face_image(pair[1], Session)
            if loaded_face_1.error is None:
                cols[1].image(loaded_face_1.face_img, caption=format_caption(loaded_face_1))
                nearest_button(cols[1], embeddings, pair[1], Session)
            else:
                cols[1].error(loaded_face_1.error)

if __name__ == "__main__":
    main()

# %%
import time
from pathlib import Path
import json
import streamlit as st
import numpy as np
from dataclasses import dataclass
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

import models
from images import cut_face, get_image, prepare_image

st.set_page_config(layout="wide")

# %%
Session = models.open_session()
vdb = models.open_lancedb()

# %%
def get_image_by_id(session, id: int) -> np.ndarray:
    with session() as session:
        image_obj = session.query(models.Image).filter(models.Image.id == id).first()
    image = get_image(Path(image_obj.best_filename))
    return prepare_image(image, 4*512), image_obj.capture_date

# %%
def get_face_image(Session, id: int, return_embedding: bool = False) -> tuple[np.ndarray, np.ndarray]:
    with Session() as session:
        face = session.query(models.Face).filter(models.Face.id == id).first()
    image, date = get_image_by_id(Session, face.image_id)
    if return_embedding:
        embedding = vdb.search().where(f"face_id == {id}").limit(1).to_list()[0]["vector"]
    fimg = cut_face(image, face)
    if return_embedding:
        return fimg, embedding, date
    else:
        return fimg, date
# %%
@dataclass
class FaceResult:
    face_id: int
    face_image: np.ndarray
    face_embedding: np.ndarray
    emb_dist: float
    date: str

def get_nearest_faces(id: int, embedding: np.ndarray, n: int = 11) -> list[FaceResult]:
    t = time.time()
    lst = vdb.search(embedding).metric("cosine").limit(n).to_list()
    print(f'VDB search time: {time.time() - t:.2f}s')
    t = time.time()
    face_results = []
    for item in lst:
        tr = time.time()
        face_image, date = get_face_image(Session, item["face_id"])
        print(f'Face image time: {time.time() - tr:.2f}s')
        f = FaceResult(
            face_id=item["face_id"],
            face_image=face_image,
            face_embedding=item["vector"],
            emb_dist=item["_distance"],
            date=date,
        )
        face_results.append(f)
    face_results = list(filter(lambda x: x.face_id != id, face_results))
    face_results.sort(key=lambda x: x.emb_dist)
    print(f'Loading time: {time.time() - t:.2f}s')
    return face_results

def get_all_face_ids(session):
    """Get all face IDs from the database"""
    with session() as sess:
        faces = sess.query(models.Face.id).all()
    return [f[0] for f in faces]

def display_face_comparison_results(results_dict):
    """Create ROC curve from collected results using matplotlib"""
    if not results_dict:
        return

    thresholds = np.linspace(0, 1, 100)
    tpr_list, fpr_list = [], []

    for threshold in thresholds:
        tp = fp = tn = fn = 0
        for _, comparisons in results_dict.items():
            for comp in comparisons:
                pred = comp['sim_dist'] <= threshold
                actual = comp['user_same_person']

                if actual and pred: tp += 1
                elif actual and not pred: fn += 1
                elif not actual and pred: fp += 1
                elif not actual and not pred: tn += 1

        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        tpr_list.append(tpr)
        fpr_list.append(fpr)

    fig, ax = plt.subplots()
    ax.plot(fpr_list, tpr_list)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve')
    ax.grid(True)

    # Add diagonal line
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5)

    st.pyplot(fig)
    plt.close()

def main():
    st.title("Face Recognition Evaluation")

    # Initialize session state
    if 'current_face_idx' not in st.session_state:
        st.session_state.current_face_idx = 0
        st.session_state.face_ids = get_all_face_ids(Session)
        st.session_state.results = defaultdict(list)

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        current_face_id = st.session_state.face_ids[st.session_state.current_face_idx]

        face_img, date = get_face_image(Session, current_face_id)
        st.image(face_img, caption=f"Face ID: {current_face_id} ({date.year})")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous") and st.session_state.current_face_idx > 0:
                st.session_state.current_face_idx -= 1
                st.rerun()
        with col2:
            if st.button("Next") and st.session_state.current_face_idx < len(st.session_state.face_ids) - 1:
                st.session_state.current_face_idx += 1
                st.rerun()

        selected_idx = st.selectbox(
            "Jump to face index:",
            range(len(st.session_state.face_ids)),
            index=st.session_state.current_face_idx
        )
        if selected_idx != st.session_state.current_face_idx:
            st.session_state.current_face_idx = selected_idx
            st.rerun()

    # Main content
    current_face_id = st.session_state.face_ids[st.session_state.current_face_idx]


    # Only compute face embeddings and nearest faces if they're not in session state
    # or if we've changed to a new face
    if ('current_nearest_faces' not in st.session_state or
        'current_face_embedding' not in st.session_state or
        'last_face_id' not in st.session_state or
        st.session_state.last_face_id != current_face_id):

        face_img, embedding, date = get_face_image(Session, current_face_id, return_embedding=True)
        nearest_faces = get_nearest_faces(current_face_id, embedding)

        st.session_state.current_nearest_faces = nearest_faces
        st.session_state.current_face_embedding = embedding
        st.session_state.last_face_id = current_face_id
    else:
        nearest_faces = st.session_state.current_nearest_faces

    # Display nearest faces and collect user input
    st.header("Nearest Faces")

    with st.form("evaluation_form", clear_on_submit=True):
        cols = st.columns(5)
        user_selections = []

        for idx, face_result in enumerate(nearest_faces):
            with cols[idx % 5]:
                st.write(f"{face_result.date.year}")
                st.image(face_result.face_image, caption=f"Face ID: {face_result.face_id}")
                st.write(f"Embedding Distance: {face_result.emb_dist:.3f}")
                user_selections.append(st.checkbox("Same Person", key=f"check_{idx}"))

        submitted = st.form_submit_button("Submit Evaluations")
        if submitted:
            st.session_state.results[current_face_id] = []
            for face_result, is_same in zip(nearest_faces, user_selections):
                st.session_state.results[current_face_id].append({
                    'compared_face_id': face_result.face_id,
                    'sim_dist': face_result.emb_dist,
                    'user_same_person': is_same
                })
            st.success("Results saved!")
            with open("face_comparison_results.json", "w") as f:
                json.dump(st.session_state.results, f)

    # Display statistics
    st.header("Evaluation Statistics")
    display_face_comparison_results(st.session_state.results)

if __name__ == "__main__":
    main()

import time
import streamlit as st
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from deepface import DeepFace
import random
from src.facerec import models
from src.facerec.detect_faces import get_image, prepare_image
import json
from collections import defaultdict

st.set_page_config(layout="wide")

RESULTS_FILE = Path("detector_results.json")
run_backends = ['retinaface', 'mtcnn', 'dlib', 'yunet', 'ssd']

def load_results():
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return {}

def save_results(results):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

def calculate_metrics(results):
    metrics = defaultdict(lambda: {
        'total': 0,
        'extra': 0,
        'missed': 0,
        'perfect': 0,
        'total_time': 0.0,  # Add timing tracking
        'successful_runs': 0  # Count only successful runs for timing average
    })

    for img_id, img_results in results.items():
        for detector, det_results in img_results.items():
            metrics[detector]['total'] += 1

            # Track timing for successful runs
            if 'processing_time' in det_results and 'error' not in det_results:
                metrics[detector]['total_time'] += det_results['processing_time']
                metrics[detector]['successful_runs'] += 1

            if det_results.get('missed_faces', False):
                metrics[detector]['missed'] += 1

            boxes = det_results.get('boxes', {})
            has_bad_box = any(not box.get('is_good', True) for box in boxes)

            if has_bad_box:
                metrics[detector]['extra'] += 1
            if not has_bad_box and not det_results.get('missed_faces', False):
                metrics[detector]['perfect'] += 1

    # Convert to percentages and include timing
    formatted_metrics = {}
    for detector, m in metrics.items():
        if m['total'] > 0:
            avg_time = m['total_time'] / m['successful_runs'] if m['successful_runs'] > 0 else 0
            formatted_metrics[detector] = {
                'extra_faces': f"{(m['extra'] / m['total']) * 100:.1f}%",
                'missed_faces': f"{(m['missed'] / m['total']) * 100:.1f}%",
                'perfect_detection': f"{(m['perfect'] / m['total']) * 100:.1f}%",
                'avg_processing_time': f"{avg_time:.2f}s",
                'total_images': m['total']
            }

    return formatted_metrics

class Timer:
    def __init__(self, label: str):
        self.label = label

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end = time.time()
        self.duration = self.end - self.start
        st.write(f"{self.label}: {self.duration:.2f} seconds")



def draw_faces(image: np.ndarray, faces: list, results: dict) -> plt.Figure:
    fig, ax = plt.subplots()
    ax.imshow(image)

    for i, face in enumerate(faces):
        x, y, w, h = [face['facial_area'][k] for k in ['x', 'y', 'w', 'h']]
        color = 'green' if results.get(f'box_{i}', {}).get('is_good', True) else 'red'
        rect = plt.Rectangle((x, y), w, h, fill=False, color=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y-5, f"Box {i+1}", color=color)

    ax.axis('off')
    return fig

def main():
    st.title("Face Detection Viewer")

    # Load saved results
    if 'detection_results' not in st.session_state:
        st.session_state.detection_results = load_results()

    # Initialize session state for images
    if 'sample_images' not in st.session_state:
        Session = models.open_session()
        with Session() as session:
            all_images = session.query(models.Image).all()
            st.session_state.sample_images = random.sample(all_images, min(100, len(all_images)))
            # Create a mapping of image IDs to images
            st.session_state.image_map = {img.id: img for img in st.session_state.sample_images}

    # # Detector selection
    # detector_backend = st.sidebar.selectbox(
    #     "Select Face Detector",
    #     ["retinaface", "mtcnn", "fastmtcnn", "dlib", "yolov8",
    #      "yunet", "centerface", "mediapipe", "ssd", "opencv"],
    #     index=0  # Default to retinaface
    # )

    max_size = st.sidebar.slider("Max Image Size", min_value=512, max_value=4096, value=2048, step=128)

    # Create selection box with image IDs
    selected_id = st.session_state.get("selected_image", st.session_state.sample_images[0].id)
    all_ids = [img.id for img in st.session_state.sample_images]
    current_index = all_ids.index(selected_id)

    # Add navigation buttons in a horizontal layout
    col1, col2, col3 = st.sidebar.columns([1, 2, 1])

    if col1.button("⬅️ Prev"):
        # Go to previous image
        new_index = (current_index - 1) % len(all_ids)
        selected_id = all_ids[new_index]
        # Update the selectbox
        st.session_state["selected_image"] = selected_id

    if col3.button("Next ➡️"):
        # Go to next image
        new_index = (current_index + 1) % len(all_ids)
        selected_id = all_ids[new_index]
        # Update the selectbox
        st.session_state["selected_image"] = selected_id

    # Update the selectbox to use session state
    selected_id = st.sidebar.selectbox(
        "Select Image",
        options=all_ids,
        index=current_index,
        format_func=lambda x: Path(st.session_state.image_map[x].best_filename).name,
        key="selected_image"  # Add this key to sync with navigation buttons
    )

    if selected_id:
        # Get the selected image object
        selected_image = st.session_state.image_map[selected_id]

        # Load and display image
        with Timer("Loading image"):
            image_path = Path(selected_image.best_filename)
            image = get_image(image_path)
            image = prepare_image(image, max_size)
        st.write(f"Image size: {image.shape}")

        if image is not None:
            st.image(image)
            # Create columns for each detector
            cols = st.columns(len(run_backends))

            # Store results for this image
            image_results = st.session_state.detection_results.setdefault(str(selected_id), {})

            for idx, detector_backend in enumerate(run_backends):
                with cols[idx]:
                    st.subheader(detector_backend)

                    detector_results = image_results.setdefault(detector_backend, {})

                    try:
                        with st.spinner('Detecting faces...'):
                            start_time = time.time()
                            try:
                                faces = DeepFace.extract_faces(
                                    image,
                                    detector_backend=detector_backend,
                                    enforce_detection=True,
                                    align=True,
                                )
                                # Store processing time in results
                                detector_results['processing_time'] = time.time() - start_time

                            except ValueError as e:
                                faces = []
                                detector_results['processing_time'] = time.time() - start_time

                        st.write(f"Found {len(faces)} faces in {detector_results['processing_time']:.2f}s")

                        # Store/update box results
                        boxes = detector_results.setdefault('boxes', [])
                        boxes.extend([{} for _ in range(len(faces) - len(boxes))])

                        # Draw faces and add checkboxes
                        fig = draw_faces(image, faces, detector_results)
                        st.pyplot(fig)

                        # Add validation UI
                        for i in range(len(faces)):
                            boxes[i]['is_good'] = st.checkbox(
                                f"Box {i+1} ({faces[i]['facial_area']['w']}x{faces[i]['facial_area']['h']}) is correct",
                                value=boxes[i].get('is_good', True),
                                key=f"{detector_backend}_{selected_id}_box_{i}"
                            )

                        detector_results['missed_faces'] = st.checkbox(
                            "Missed some faces?",
                            value=detector_results.get('missed_faces', False),
                            key=f"{detector_backend}_{selected_id}_missed"
                        )

                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        detector_results['error'] = str(e)

            # Save results after each update
            save_results(st.session_state.detection_results)

            # Display metrics
            st.subheader("Detection Quality Metrics")
            metrics = calculate_metrics(st.session_state.detection_results)
            st.table(metrics)
        else:
            st.error(f"Could not load image: {image_path}")

if __name__ == "__main__":
    main()
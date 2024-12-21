# %%
from pathlib import Path
import json
import numpy as np
import lancedb
import tqdm
import pyarrow as pa
from insightface.app import FaceAnalysis

import models
import images

analyzer = FaceAnalysis(providers=['CPUExecutionProvider'])
analyzer.prepare(ctx_id=0, det_size=(640, 640))

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.int64):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


# %%
def get_unprocessed_images(session) -> list[int]:
    """
    Get all image ids that have no associated face detection runs.

    Args:
        session: SQLAlchemy session object

    Returns:
        list[int]: List of image ids that have no face detection runs
    """
    # Query for images that don't have any detection runs
    unprocessed = session.query(models.Image).outerjoin(
        models.FaceDetectionRun
    ).filter(
        models.FaceDetectionRun.id == None
    ).all()

    return [image.id for image in unprocessed]


def process_image(image_id: int, session: models.sessionmaker, lance_table) -> int:
    image_obj = session.query(models.Image).get(image_id)
    image_path = Path(image_obj.best_filename)
    image: np.ndarray = images.get_image(image_path)
    faces = []
    if image is not None:
        try:
            if image.ndim == 3:
                faces = analyzer.get(image[:,:,::-1])
            if image.ndim == 2:
                faces = analyzer.get(image)
        except ValueError:
            faces = []
    else:
        print(f"No image loaded for {image_path}")

    detection_run = models.FaceDetectionRun(
        image_id=image_obj.id,
        source_filename=str(image_path),
        detection_algorithm='insightface',
        embedding_model='insightface',
        num_faces=len(faces),
    )
    session.add(detection_run)
    session.flush()
    if len(faces) == 0:
        # print(f"No faces found in {image_path}")
        session.commit()
        return 0
    face_objs = []
    embeddings = []
    for face in faces:
        x, y, w, h = face.bbox[0], face.bbox[1], face.bbox[2]-face.bbox[0], face.bbox[3]-face.bbox[1]
        embedding = face.embedding
        delattr(face, 'embedding')
        face_obj = models.Face(
            detection_run_id=detection_run.id,
            image_id=image_obj.id,
            img_width=image.shape[1],
            img_height=image.shape[0],
            x=int(x), y=int(y), w=int(w), h=int(h),
            face_data=json.dumps(face, cls=NumpyEncoder),
        )
        face_objs.append(face_obj)
        assert len(embedding) == 512, f"Expected 512, got {len(embedding)}: {embedding}"
        embeddings.append({"vector": embedding, "face_id": None})
    session.add_all(face_objs)
    session.commit()
    for i, embedding in enumerate(embeddings):
        embedding['face_id'] = face_objs[i].id
    lance_table.add(embeddings)
    return len(faces)
# %%
def process_new_images(Session: models.sessionmaker, lance_table) -> None:
    with Session() as session:
        image_ids = get_unprocessed_images(session)
    progress = tqdm.tqdm(total=len(image_ids), desc="Processing images")
    total_faces = 0
    for image_id in image_ids:
        with Session() as session:
            num_faces = process_image(image_id, session, lance_table)
            progress.update(1)
            total_faces += num_faces
            progress.set_postfix(faces=total_faces)
    progress.close()
    print(f"Processed {total_faces} faces")


# %%
def create_lancedb_table() -> lancedb.table.Table:
    schema = pa.schema([
        pa.field("vector", pa.list_(pa.float32(), list_size=512)),
        pa.field("face_id", pa.int64()),
    ])
    # Synchronous client
    db = lancedb.connect(".")
    return db.create_table("faces", schema=schema, exist_ok=True)


# %%
if __name__ == '__main__':
    Session = models.open_session()
    lance_table = create_lancedb_table()
    process_new_images(Session, lance_table)


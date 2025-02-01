from pathlib import Path
from datetime import datetime
import numpy as np
import tqdm
from insightface.app import FaceAnalysis

from facerec import models
from facerec import images

analyzer = FaceAnalysis(providers=['CPUExecutionProvider'])
analyzer.prepare(ctx_id=0, det_size=(640, 640))

def process_image(image_id: int, ctx: models.Context) -> int:
    image_obj = ctx.images.images[image_id]
    image_path = Path(image_obj.best_filename)
    image: np.ndarray | None = images.get_image(image_path)
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

    image_obj.faces_detected_at = datetime.now()
    if len(faces) == 0:
        return 0

    for face in faces:
        x, y, w, h = face.bbox[0], face.bbox[1], face.bbox[2]-face.bbox[0], face.bbox[3]-face.bbox[1]
        emb: np.ndarray = face.embedding
        face.embedding = None
        face_obj = models.Face(
            id=0,  # id will be set by the database
            image_id=image_obj.id,
            img_width=image.shape[1],
            img_height=image.shape[0],
            x=int(x), y=int(y), w=int(w), h=int(h),
            emb=emb.tolist(),
            face_data=str(face),
        )
        ctx.faces.add(face_obj)

        face_img = images.cut_face(image, face_obj)
        ctx.save_extracted_face(face_obj.id, face_img)
    return len(faces)
# %%
def process_new_images(data_root: Path, force: bool = False) -> None:
    ctx = models.Context(data_root)

    image_ids = [img.id for img in ctx.images.images.values() if img.faces_detected_at is None or force]

    progress = tqdm.tqdm(total=len(image_ids), desc="Processing images")
    total_faces = 0
    for i, image_id in enumerate(image_ids):
        num_faces = process_image(image_id, ctx)
        progress.update(1)
        total_faces += num_faces
        progress.set_postfix(faces=total_faces)
        if i % 100 == 0:
            ctx.save()
    progress.close()
    print(f"Processed {total_faces} faces")
    ctx.save()


# %%
if __name__ == '__main__':
    process_new_images(Path('d'))


from pathlib import Path
import numpy as np
from tqdm import tqdm
import cv2

import models
from images import get_image, prepare_image, cut_face

def extract_faces():
    # Create output directory
    output_dir = Path("faces_extr")
    output_dir.mkdir(exist_ok=True)

    Session = models.open_session()

    with Session() as session:
        # Get all faces with their associated images, sorted by image_id
        faces = session.query(models.Face, models.Image).join(
            models.Image, models.Face.image_id == models.Image.id
        ).order_by(models.Face.image_id).all()


        # Cache variables
        last_image_id = None
        last_img = None

        # Process each face
        for face, image in tqdm(faces, desc="Extracting faces"):
            # Only load image if it's different from the last one
            if last_image_id != image.id:
                img = get_image(Path(image.best_filename))
                img = prepare_image(img, 4*512)
                last_image_id = image.id
                last_img = img

            # Cut out the face using cached image
            face_img = cut_face(last_img, face)

            # Save the face image
            output_path = output_dir / f"face_{face.id}.jpg"
            face_img_bgr = face_img[..., ::-1]
            cv2.imwrite(str(output_path), face_img_bgr)

if __name__ == "__main__":
    extract_faces()

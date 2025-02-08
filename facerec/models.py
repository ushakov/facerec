from pathlib import Path
from datetime import datetime
import cv2
from pydantic import BaseModel
import numpy as np
from collections import defaultdict
RAW_EXTENSIONS = {'.nef', '.arw'}
JPG_EXTENSIONS = {'.jpg', '.jpeg'}

class Image(BaseModel):
    id: int
    key: str
    best_filename: str
    capture_date: datetime | None
    discovered_at: datetime
    faces_detected_at: datetime | None = None


class File(BaseModel):
    id: int
    image_id: int
    filename: str
    discovered_at: datetime


class Face(BaseModel):
    id: int
    image_id: int
    img_width: int
    img_height: int
    x: int
    y: int
    w: int
    h: int
    emb: list[float] | None
    face_data: str


class Component(BaseModel):
    id: int
    faces: list[int]


class Images:
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.images = self.read()
        self.next_id = max(self.images.keys()) + 1 if self.images else 1

    def read(self) -> dict[int, Image]:
        fname = self.data_root / 'images.jsonl'
        if not fname.exists():
            return {}
        with open(fname, 'r') as f:
            images = {}
            for line in f:
                img = Image.model_validate_json(line)
                images[img.id] = img
            return images

    def write(self) -> None:
        fname = self.data_root / 'images.jsonl'
        with open(fname, 'w') as f:
            for img in self.images.values():
                f.write(img.model_dump_json() + '\n')

    def add(self, image: Image) -> None:
        if image.id == 0:
            image.id = self.next_id
            self.next_id += 1
        self.images[image.id] = image
        self.write()


class Faces:
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.faces = self.read()
        self.next_id = max(self.faces.keys()) + 1 if self.faces else 1

    def read(self) -> dict[int, Face]:
        fname = self.data_root / 'faces.jsonl'
        if not fname.exists():
            return {}
        with open(fname, 'r') as f:
            faces = {}
            for line in f:
                face = Face.model_validate_json(line)
                faces[face.id] = face
            return faces

    def write(self) -> None:
        fname = self.data_root / 'faces.jsonl'
        with open(fname, 'w') as f:
            for face in self.faces.values():
                f.write(face.model_dump_json() + '\n')

    def add(self, face: Face) -> None:
        if face.id == 0:
            face.id = self.next_id
            self.next_id += 1
        self.faces[face.id] = face

class Context:
    def __init__(self, data_root: Path):
        print(data_root)
        self.data_root = data_root
        (data_root / 'faces_extr').mkdir(exist_ok=True, parents=True)
        self.images = Images(data_root)
        self.faces = Faces(data_root)
        self.img2faces = defaultdict(list)
        for face in self.faces.faces.values():
            self.img2faces[face.image_id].append(face.id)

    def save(self) -> None:
        self.save_images()
        self.save_faces()

    def save_images(self) -> None:
        self.images.write()

    def save_faces(self) -> None:
        self.faces.write()

    def save_extracted_face(self, id: int, face: np.ndarray) -> None:
        fname = self.data_root / 'faces_extr' / f'face_{id}.jpg'
        face_img_bgr = face[..., ::-1]
        cv2.imwrite(str(fname), face_img_bgr)

    def get_embeddings(self) -> tuple[np.ndarray, list[int]]:
        face_ids = sorted(self.faces.faces.keys())
        r = []
        for id in face_ids:
            r.append(self.faces.faces[id].emb)
        faces = np.array(r)
        faces = faces / np.linalg.norm(faces, axis=1)[:, None]
        return faces, face_ids

    def get_faces_in_image(self, image_id: int) -> list[int]:
        return self.img2faces[image_id]

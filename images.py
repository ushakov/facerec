import io
from pathlib import Path
import numpy as np
import rawpy
from PIL import Image, ImageOps
from skimage.transform import rescale
import models

def rescale_to_max(image: np.ndarray, max_size: int) -> np.ndarray:
    h, w = image.shape[:2]
    scale = max_size / max(h, w)
    scale = min(scale, 1)
    rescaled = rescale(image, scale, anti_aliasing=False, channel_axis=-1)
    return rescaled

def get_initial_thumb_image(raw: rawpy.RawPy) -> np.ndarray:
    try:
        rgb = raw.extract_thumb()
    except Exception as e:
        image = np.array(raw.postprocess())
        return image
    if rgb.format == rawpy.ThumbFormat.JPEG:
        image = Image.open(io.BytesIO(rgb.data))
        image = np.array(image)
    elif rgb.format == rawpy.ThumbFormat.BITMAP:
        image = rgb.data
    return image

def rot_ccw(image: np.ndarray) -> np.ndarray:
    return image.transpose(1, 0, 2)[::-1, :, :]

def rot_cw(image: np.ndarray) -> np.ndarray:
    return image.transpose(1, 0, 2)[:, ::-1, :]

def rot_180(image: np.ndarray) -> np.ndarray:
    return image[::-1, ::-1, :]

def get_thumb_image(path: Path) -> np.ndarray:
    with rawpy.imread(str(path)) as raw:
        raw: rawpy.RawPy = raw
        image = get_initial_thumb_image(raw)
        if raw.sizes.flip == 3:
            image = rot_180(image)
        elif raw.sizes.flip == 5:
            image = rot_ccw(image)
        elif raw.sizes.flip == 6:
            image = rot_cw(image)
    return image

def get_jpeg_image(path: Path) -> np.ndarray:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    arr = np.array(img)
    return arr

def get_image(path: Path) -> np.ndarray | None:
    try:
        if path.suffix.lower() in models.RAW_EXTENSIONS:
            image = get_thumb_image(path)
        if path.suffix.lower() in models.JPG_EXTENSIONS:
            image = get_jpeg_image(path)
        return image
    except Exception as e:
        print(f"Error loading image {path}: {e}")
    return None

def prepare_image(image: np.ndarray, max_size: int) -> np.ndarray:
    image = rescale_to_max(image, max_size)
    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8)
    return image

def cut_face(image: np.ndarray, face: models.Face) -> np.ndarray:
    scale_x = image.shape[1] / face.img_width
    scale_y = image.shape[0] / face.img_height

    x = int((face.x - face.w/2)*scale_x)
    y = int((face.y - face.h/2)*scale_y)
    w = int(2*face.w*scale_x)
    h = int(2*face.h*scale_y)

    x = max(x, 0)
    y = max(y, 0)
    w = min(w, image.shape[1] - x)
    h = min(h, image.shape[0] - y)

    return image[y:y+h, x:x+w]

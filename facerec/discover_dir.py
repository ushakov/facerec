from pathlib import Path
from datetime import datetime
import exifread
import tqdm

from facerec import models


def get_capture_date(filepath: Path) -> datetime | None:
    """Extract capture date from image file metadata."""
    try:
        with open(filepath, 'rb') as img_file:
            img = exifread.process_file(img_file)
            date = None
            if 'EXIF DateTimeOriginal' in img:
                date = datetime.strptime(img['EXIF DateTimeOriginal'].values, '%Y:%m:%d %H:%M:%S').date()
            elif 'EXIF DateTimeDigitized' in img:
                date = datetime.strptime(img['EXIF DateTimeDigitized'].values, '%Y:%m:%d %H:%M:%S').date()
            elif 'EXIF DateTime' in img:
                date = datetime.strptime(img['EXIF DateTime'].values, '%Y:%m:%d %H:%M:%S').date()
            return date
    except Exception as e:
        print(f"Error reading date from {filepath}: {e}")
    return None


def find_files(img_root: Path, data_root: Path) -> tuple[dict[Path, list[Path]], dict[str, list[Path]]]:
    ctx = models.Context(data_root)
    root = Path(img_root)
    new_images = 0
    progress = tqdm.tqdm(desc='Discovering files')
    for path, _, files in root.walk():
        for file in files:
            progress.update(1)
            pf = Path(path / file).absolute()
            ext = pf.suffix.lower()
            idx = pf.with_suffix('')
            if ext not in models.RAW_EXTENSIONS and ext not in models.JPG_EXTENSIONS:
                continue

            if str(idx) not in ctx.images.images:
                capture_date = get_capture_date(pf)
                img = models.Image(
                    id=0,  # id will be set by the database
                    key=str(idx),
                    best_filename=str(pf),
                    capture_date=capture_date,
                    discovered_at=datetime.now()
                )
                ctx.images.add(img)
                new_images += 1
    ctx.save()
    print(f'Number of new images: {new_images}')

if __name__ == '__main__':
    root = Path('/home/ushakov/photo/master/Archive-2012')
    data_root = Path('d')
    find_files(root, data_root)

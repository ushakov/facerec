# %%
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import exifread
import tqdm

from models import open_session, Image, File, RAW_EXTENSIONS, JPG_EXTENSIONS


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

def find_files(path: Path, Session: sessionmaker) -> tuple[dict[Path, list[Path]], dict[str, list[Path]]]:
    session = Session()
    prev_images = session.query(Image).all()
    images = {
        img.key: img
        for img in prev_images
    }
    root = Path(path)
    new_images = 0
    new_files = 0
    progress = tqdm.tqdm(desc='Discovering files')
    for path, _, files in root.walk():
        for file in files:
            progress.update(1)
            pf = Path(path / file).absolute()
            ext = pf.suffix.lower()
            idx = pf.with_suffix('')
            if ext not in RAW_EXTENSIONS and ext not in JPG_EXTENSIONS:
                continue

            if str(idx) not in images:
                capture_date = get_capture_date(pf)
                img = Image(
                    key=str(idx),
                    best_filename=str(pf),
                    capture_date=capture_date
                )
                session.add(img)
                session.flush()
                images[str(idx)] = img
                new_images += 1

            if session.query(File).filter_by(filename=str(pf)).first() is None:
                file = File(image_id=images[str(idx)].id, filename=str(pf))
                session.add(file)
                new_files += 1
        session.flush()
    print(f'Number of new images: {new_images}')
    print(f'Number of new files: {new_files}')
    session.commit()

# %%
if __name__ == '__main__':
    root = Path('/home/ushakov/photo/master')
    Session = open_session()
    find_files(root, Session)

from pathlib import Path
import lancedb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

RAW_EXTENSIONS = {'.nef', '.arw'}
JPG_EXTENSIONS = {'.jpg', '.jpeg'}

Base = declarative_base()

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    best_filename = Column(String, unique=True, nullable=False)
    capture_date = Column(DateTime, nullable=True)
    discovered_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        best_fn = str(self.best_filename).removeprefix(str(self.key))
        return f"<Image(id={self.id}, key='{self.key}', best_filename='{best_fn}')>"


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    filename = Column(String, unique=True, nullable=False)
    discovered_at = Column(DateTime, default=datetime.now)


class FaceDetectionRun(Base):
    __tablename__ = 'face_detection_runs'

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    source_filename = Column(String, nullable=False)
    detected_at = Column(DateTime, default=datetime.now)
    detection_algorithm = Column(String, nullable=False)
    embedding_model = Column(String, nullable=False)
    num_faces = Column(Integer, nullable=False)


class Face(Base):
    __tablename__ = 'faces'

    id = Column(Integer, primary_key=True)
    detection_run_id = Column(Integer, ForeignKey('face_detection_runs.id'), nullable=False)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    img_width = Column(Integer, nullable=False)
    img_height = Column(Integer, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    w = Column(Integer, nullable=False)
    h = Column(Integer, nullable=False)
    face_data = Column(String, nullable=False)

Index('idx_key', Image.key)
Index('idx_filename', File.filename)
Index('idx_detection_run_image', FaceDetectionRun.image_id)


def open_session() -> sessionmaker:
    # Create the engine and tables
    engine = create_engine(f'sqlite:///discovered_files.db')
    Base.metadata.create_all(engine)

    # Create a session factory
    return sessionmaker(bind=engine)

def open_lancedb() -> lancedb.table.Table:
    db = lancedb.connect(".")
    return db.open_table("faces")

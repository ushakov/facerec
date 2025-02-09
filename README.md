# FaceRec

FaceRec is a face recognition and clustering tool that helps you organize and analyze faces in your photo collection. It uses state-of-the-art deep learning models from InsightFace for face detection and recognition, and provides an interactive web interface for exploring face clusters.

## Features

- Automatic face detection in photos
- Face embedding extraction using advanced neural networks
- Intelligent face clustering
- Web interface for exploring and organizing face clusters
- CPU-friendly (no GPU required)

## Installation

FaceRec can be easily installed using `pipx`:

```bash
pipx install git+https://github.com/ushakov/facerec.git
```

## Dependencies

FaceRec requires Python 3.10 or later and uses the following main dependencies (installed automatically by `pipx`):
- insightface
- numpy
- networkx
- FastAPI (for web interface)
- uvicorn
- tqdm
- jsonargparse

## Usage

FaceRec provides a simple command-line interface with several commands:

1. **Discover photos**:
```bash
facerec --data_dir /path/to/database discover /path/to/photos
```
This command will scan the source directory for images and prepare them for processing.

2. **Detect faces**:
```bash
facerec --data_dir /path/to/database detect
```
This will process all discovered images, detect faces, and extract face embeddings.

3. **Cluster faces**:
```bash
facerec --data_dir /path/to/database cluster
```
This command will analyze all detected faces and group them into clusters based on similarity.

4. **Launch web interface**:
```bash
facerec --data_dir /path/to/database serve
```
This will start a web server on port 8000 where you can explore and organize the face clusters.

## Web Interface Usage

The web interface provides several views to explore and organize your face collection:

1. **Face Explorer** (`/faces`)
   - Browse random faces from your collection
   - Click on any face to see similar faces along with the context image
   - View similarity scores between faces
   - Navigate to different face clusters

2. **Components** (`/components`)
   - View and manage face clusters
   - Assign people to clusters
   - Propose and manage cluster subdivisions
   - See component sizes and relationships

3. **People Management** (`/people`)
   - Search through known people
   - Organize your photo collection by person

### Navigation and Common Actions

- **Top Navigation Bar**: Use the navigation bar to switch between main views (Explore, Components, People)
- **Component View**:
  - Click "Load Random Component" to view a different face cluster
  - Use "Assign Person" to link a person to all faces in the component
  - Click "Propose Subdivision" if you notice different people in the same cluster
- **Face Explorer**:
  - Click "Shuffle Faces" to view different random faces
  - Click any face to see similar faces across your collection
  - When viewing similar faces, similarity scores are shown for each match
- **People View**:
  - Use the search bar to find existing people
  - Click the "+" button to add a new person
  - Each person card shows their name and allows deletion

## How it Works

1. The discovery phase scans your photo directory and creates a database of images. (NEF, ARW, JPG images are supported)
2. Face detection uses InsightFace's face analyzer to detect faces in each image and extract high-dimensional embeddings.
3. The clustering phase builds a similarity graph between faces and uses the Louvain community detection algorithm to group similar faces together.
4. The web interface allows you to explore these clusters, helping you organize and label faces in your photo collection.

## Data Storage

FaceRec stores its database and processed faces in the specified data directory with the following structure:
- `images.jsonl`: Database of discovered images
- `faces.jsonl`: Database of detected faces
- `faces_extr/`: Directory containing extracted face thumbnails
- `face_similarity.gexf`: Face similarity graph
- `louvain_communities.json`: Computed face clusters
- `people.json`: People database
- `component_people.json`: Component-person assignments


# Face Recognition System

This project implements a face recognition pipeline using simple, file-based storage.

## Overview

The system performs four main tasks:

1. **Discover**: Scans directories for RAW (.nef, .arw) and JPEG images, extracts metadata (e.g., capture date from EXIF), and stores records in JSON Lines files (images.jsonl, faces.jsonl).

2. **Detect**: Processes images to detect faces and compute 512-dimensional embeddings using InsightFace.

3. **Cluster**: Builds a cosine similarity graph (threshold: 0.4) from face embeddings and applies Louvain community detection. The graph is saved as a GEXF file with communities stored in JSON.

4. **Serve**: Runs a FastAPI (GraphWalk) backend to explore face clusters and perform similarity searches.

## Data Storage

- **Metadata**: JSONL files in a configurable data directory (e.g., images.jsonl, faces.jsonl).
- **Face Images**: Extracted face crops are saved in a dedicated folder (faces_extr).
- **Similarity Graphs**: Stored in GEXF format, with community detection results in a JSON file.

## Key Files

- **models.py**: Defines data models and file-based storage classes.
- **discover_dir.py**: Handles image discovery and metadata extraction.
- **detect_faces.py**: Implements face detection and embedding extraction.
- **cluster_faces.py**: Constructs the similarity graph and clusters faces.
- **facerec.py**: Main CLI entry point to run discovery, detection, clustering, and serving.
- **images.py**: Contains image processing utilities (e.g., thumbnail generation, image normalization).
- **graphwalk/backend/**: Contains the FastAPI backend for the web interface.
- **graphwalk/frontend/**: Contains the web frontend code.

### Frontend

Tech Stack Used: React, TypeScript, Tailwind CSS, DaisyUI, Framer Motion, React Router, Vite.

1. **Core Views**:
   - `ExploreView`: Main interface for browsing and exploring faces, with similarity search
   - `ComponentView`: Displays face clusters and community detection results
   - `PeopleView`: Manages labeled individuals and their associated faces

2. **Key Components**:
   - `Face`: Renders individual face crops with metadata and interactions
   - `FaceGrid`: Displays collections of faces in a responsive grid layout
   - `PersonCard`: Shows person details with their associated faces
   - `ImageContext`: Provides the original image context for detected faces
   - `PersonSearchDropdown`: Enables quick person search and selection

3. **API Integration**:
   - API calls are centralized in the `api` directory
   - Handles face fetching, similarity searches, and person management
   - Maintains type safety with TypeScript interfaces matching backend models

The application uses React Router for navigation and Framer Motion for smooth transitions between views. The UI is built with Tailwind CSS and DaisyUI components, providing a modern and responsive interface for exploring the face recognition system.

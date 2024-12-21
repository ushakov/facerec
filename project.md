# Face Recognition System

## Architecture

### Data Storage
- SQLite database (`discovered_files.db`) for metadata and relationships
- LanceDB for vector embeddings storage and similarity search
- GEXF files for face similarity graphs

### Core Components

#### Image Management
- Tracks both RAW (`.nef`, `.arw`) and JPEG images
- Associates multiple files with single logical image
- Records capture dates and discovery timestamps

#### Face Detection & Analysis
- Uses InsightFace for face detection and embedding generation
- CPU execution provider for compatibility
- 512-dimensional face embeddings
- Stores face bounding boxes and metadata

#### Similarity Analysis
- Cosine similarity-based face comparison
- Graph-based clustering (NetworkX)
- Distance threshold: 0.4 for edge creation
- Community detection using Louvain method

### Web Interface (GraphWalk)

#### Backend (FastAPI)
- Face similarity search with bucketed sampling
- Component exploration and comparison
- People management with fuzzy search
- Image serving for detected faces
- CORS support for local development

#### Frontend (React + TypeScript)
- Modern stack: Vite, React, TypeScript, Tailwind CSS
- Component-based architecture:
  - Views:
    - `ExploreView`: Random face exploration
    - `ComponentView`: Cluster visualization
    - `CompareView`: Side-by-side cluster comparison
    - `PeopleView`: Person management interface
  - Components:
    - `Face`: Face display with metadata
    - `FaceGrid`: Grid layout for face collections
    - `PersonSearchDropdown`: Autocomplete person search
    - `Layout`: Common page structure
  - API Layer:
    - `faces.ts`: Backend API client implementation

#### API Features
- Random face sampling
- Similar face discovery with distance bucketing
- Component navigation and comparison
- Person management with multi-strategy search:
  - Prefix matching
  - Initials matching
  - Fuzzy name search

### Data Models

#### Database Schema
- `images`: Core image metadata
- `files`: Physical file locations
- `face_detection_runs`: Detection job tracking
- `faces`: Detected face regions and metadata

#### Vector Store
- LanceDB table schema:
  - `vector`: float32[512] face embeddings
  - `face_id`: int64 reference to SQL faces table

### Key Files
- `detect_faces.py`: Face detection pipeline
- `build_graph.py`: Similarity graph construction
- `models.py`: Data models and DB interface
- `communty_analysis.py`: Face clustering logic

### Processing Pipeline
1. Image discovery and indexing
2. Face detection and embedding extraction
3. Similarity graph construction
4. Community detection for face clustering

## Major APIs

### Face Detection (`detect_faces.py`)
- `FaceAnalysis.get()`: InsightFace detection and embedding
- `process_image()`: Face detection and metadata extraction
- `Face` model: Stores bbox, landmarks, embedding (512d)

### Graph Construction (`build_graph.py`)
- `FaceGraph.build_graph()`: Constructs similarity network
  - Input: Face embeddings matrix
  - Output: NetworkX graph with distance weights

### Community Analysis (`communty_analysis.py`)
- Louvain community detection
- Component filtering and analysis
- Graph metrics calculation

### REST API (`graphwalk/backend/main.py`)
- Face Endpoints:
  - `GET /random-faces`: Sample random face IDs
  - `GET /similar-faces/{face_id}`: Find similar faces with bucketing
  - `GET /face/{face_id}`: Serve face image
- Component Endpoints:
  - `GET /random_component`: Get random cluster
  - `GET /component/{comp_id}`: Get cluster details and neighbors
  - `GET /compare-components/{comp_id1}/{comp_id2}`: Find similar faces between clusters
- Person Management:
  - `POST /people`: Create person
  - `GET /people`: List all people
  - `GET /people/search`: Multi-strategy name search

### Database Models (`models.py`)
- Table Operations:
  - `Image`: `best_filename`, `capture_date`
  - `File`: `filename`, `image_id`
  - `FaceDetectionRun`: Detection metadata
  - `Face`: Face region and embedding data

## Implementation Details

### Frontend Architecture

#### View Components
- `ExploreView`:
  - Random face sampling and exploration
  - Similar face discovery with distance bucketing
- `ComponentView`:
  - Cluster visualization and navigation
  - Neighbor cluster exploration
- `CompareView`:
  - Side-by-side cluster comparison
  - Similar face pair identification
- `PeopleView`:
  - Person management and tagging
  - Multi-strategy name search interface

#### Reusable Components
- `Face`:
  - Face image display
  - Metadata overlay
  - Click handlers for navigation
- `FaceGrid`:
  - Responsive grid layout
  - Uniform face card presentation
- `PersonSearchDropdown`:
  - Autocomplete search interface
  - Multi-strategy name matching
- `Layout`:
  - Common navigation structure
  - Consistent page layout

#### API Integration
- TypeScript interfaces for type safety
- Centralized API client in `faces.ts`
- Error handling and response typing
- Endpoint abstraction for:
  - Face operations
  - Component comparison
  - Person management
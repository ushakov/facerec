# Backend Implementation Documentation

## Core Components
- FastAPI application with CORS middleware
- Face embedding processing and similarity search
- Component-based face clustering
- People management system

## Data Structures
- Face embeddings: numpy arrays normalized for cosine similarity
- Face IDs: mapped to component clusters
- Components: JSON-based clusters of related faces
- People: JSON-based storage of person records

## Key APIs

### Face Operations
- `GET /random-faces`: Returns random face IDs
- `GET /similar-faces/{face_id}`: Returns similar faces using bucketed cosine similarity
- `GET /face/{face_id}`: Serves face image files

### Component Operations
- `GET /random_component`: Returns random component ID
- `GET /component/{comp_id}`: Returns component details with:
  - Size
  - Sample photos
  - Neighboring components
- `GET /compare-components/{comp_id1}/{comp_id2}`: Finds most similar face pairs between components

### People Management
- `GET /people`: Lists all people
- `POST /people`: Creates new person
- `GET /people/search`: Multi-strategy name search:
  - Prefix matching (highest priority)
  - Initials matching
  - Fuzzy matching (lowest priority)

## Data Formats

### Face Similarity Response
```typescript
{
  id: string
  component_id: string | null
  similarity: float
}
```

### Person Object
```typescript
{
  id: number
  name: string
}
```

### Component Response
```typescript
{
  size: number
  photos: string[]
  neighbors: {
    comp_id: string
    size: number
    sample_face_id: string
    distance: number
  }[]
}
```

## Configuration
- Subgraph directory and suffix configurable via Settings
- CORS enabled for localhost:5173
- Face data loaded from NPZ files
- Component data from JSON files
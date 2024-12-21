# GraphWalk Frontend Documentation

## Architecture

### Tech Stack
- React + TypeScript
- Tailwind CSS + DaisyUI
- Framer Motion for animations
- React Router for navigation

### Directory Structure
```
src/
├── api/         # API client code
├── components/  # Reusable UI components
├── views/       # Page components
├── assets/      # Static assets
└── App.tsx      # Root component
```

## Core Features

### Face Exploration
- Random face browsing
- Similar face discovery
- Face similarity scoring
- Component-based clustering

### Data Types
```typescript
interface FaceWithSimilarity {
    id: string
    component_id: string
    similarity?: number
}

interface FacePair {
    distance: number
    face1_id: string
    face2_id: string
}

interface Person {
    id: number
    name: string
}
```

### API Endpoints
- Base URL: `http://localhost:8000`

#### Face Operations
- `/face/{id}` - Get face image
- `/random-faces?count={n}` - Get n random faces
- `/similar-faces/{id}?count={n}&per_bucket={m}` - Get similar faces
- `/compare-components/{id1}/{id2}` - Compare face components
- `/component/{id}` - Get component details
- `/random_component` - Get random component

#### People Operations
- GET `/people` - List people
- POST `/people` - Create person

## Views

### ExploreView (`/faces`, `/faces/:id`)
- Browse random faces
- View similar faces for selected face
- Similarity scoring display

### ComponentView (`/components`, `/components/:id`)
- View face clusters
- Component size information
- Similar component suggestions
- Component comparison links

### CompareView (`/compare/:id1/:id2`)
- Side-by-side face comparison
- Distance metrics display
- Animated transitions

### PeopleView (`/people`)
- Person management
- Search functionality
- CRUD operations

## UI Components

### Key Components
- `Face` - Face display with hover effects
- `FaceGrid` - Grid layout for faces
- `PersonSearchDropdown` - Autocomplete search
- `Layout` - Common page structure

### Features
- Responsive design
- Loading states
- Animated transitions
- Interactive hover effects
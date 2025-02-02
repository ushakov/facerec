import math
import json
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
import random
import networkx as nx
from pydantic import BaseModel
from heapq import nsmallest
from itertools import product
from fuzzywuzzy import process
from importlib.resources import files

from facerec import models


@dataclass
class Settings:
    static_root = files('facerec')
    subgraph_dir: Path = Path(".")

settings = Settings()

app = FastAPI()

# Mount static files
app.mount("/assets", StaticFiles(directory=str(settings.static_root / "graphwalk/frontend/dist/assets")), name="assets")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FACES_DIR = None
faces = None
face_ids = None
face_ctx = None

components = None
face_to_component = None
graph = None
subgraph = None

def load_graph():
    global graph
    if graph is None:
        graph = nx.read_gexf(str(settings.subgraph_dir / "face_similarity.gexf"))


@app.on_event("startup")
async def load_data():
    global FACES_DIR, face_ctx, faces, face_ids, components, face_to_component, PEOPLE_FILE, COMPONENT_PEOPLE_FILE, people, component_people
    FACES_DIR = settings.subgraph_dir / "faces_extr"
    face_ctx = models.Context(settings.subgraph_dir)
    faces, face_ids = face_ctx.get_embeddings()
    components = []
    face_to_component = {}

    with open(settings.subgraph_dir / f"louvain_communities.json", 'r') as f:
        components = json.load(f)
    face_to_component = {face_id: i for i, component in enumerate(components) for face_id in component}

    PEOPLE_FILE = settings.subgraph_dir / "people.json"
    COMPONENT_PEOPLE_FILE = settings.subgraph_dir / "component_people.json"
    people = {}
    component_people = {}
    if PEOPLE_FILE.exists():
        with open(PEOPLE_FILE, 'r') as f:
            data = json.load(f)
            for k, v in data.items():
                people[int(k)] = Person(id=int(k), name=v)
    if COMPONENT_PEOPLE_FILE.exists():
        with open(COMPONENT_PEOPLE_FILE, 'r') as f:
            data = json.load(f)
            for k, v in data.items():
                component_people[int(k)] = int(v)

class FaceWithSimilarity(BaseModel):
    id: int
    component_id: int | None
    person_name: str | None
    similarity: float

class Person(BaseModel):
    id: int
    name: str

class PersonCreate(BaseModel):
    name: str

class ComponentPerson(BaseModel):
    person_id: int

def save_people():
    """Persist people database to disk"""
    with open(PEOPLE_FILE, 'w') as f:
        json.dump({k: v.name for k, v in people.items()}, f)

def save_component_people():
    """Persist component-person assignments to disk"""
    with open(COMPONENT_PEOPLE_FILE, 'w') as f:
        json.dump({k: v for k, v in component_people.items()}, f)

@app.get("/random-faces")
async def get_random_faces(count: int = 20) -> List[str]:
    """Get random face IDs"""
    indices = random.sample(range(len(face_ids)), min(count, len(face_ids)))
    return [str(face_ids[i]) for i in indices]

class SimilarFacesResponse(BaseModel):
    query_face: FaceWithSimilarity
    similar_faces: List[FaceWithSimilarity]

def create_face_with_similarity(face_id: int, similarity: float = 0.0) -> FaceWithSimilarity:
    """Helper function to create FaceWithSimilarity objects with component and person info"""
    component_id = face_to_component.get(face_id)
    person_name = None
    if component_id is not None and component_id in component_people:
        person_id = component_people[component_id]
        person_name = people[person_id].name

    return FaceWithSimilarity(
        id=str(face_id),
        similarity=similarity,
        component_id=component_id,
        person_name=person_name
    )

@app.get("/similar-faces/{face_id}", response_model=SimilarFacesResponse)
async def get_similar_faces(face_id: int, count: int = 20, per_bucket: int = 5) -> SimilarFacesResponse:
    """Get similar faces based on embedding distance"""
    try:
        idx = face_ids.index(face_id)
        vec = faces[idx]

        # Create query face response
        query_face = create_face_with_similarity(face_id)

        # Calculate cosine similarities
        distances = 1 - np.dot(faces, vec)
        most_similar = np.argsort(distances)

        bucket_list = [[] for _ in range(9)]
        for num, i in enumerate(most_similar):
            dist = float(distances[i])  # Convert to Python float
            if dist > 0.6:
                print(f"done processing {num} faces, cur dist {dist}")
                break
            if dist < 0.1:
                print(f"Skipping {num}th most similar face with distance {dist}")
                continue
            bucket_idx = int(math.floor(dist / 0.1)-1)
            bucket_list[bucket_idx].append((i, dist))

        res = []
        for bucket in bucket_list:
            if len(bucket) > 0:
                sample = random.sample(bucket, min(count, len(bucket)))
                for idx, dist in sample:
                    res.append(create_face_with_similarity(face_ids[idx], dist))
            if len(res) >= count:
                return SimilarFacesResponse(query_face=query_face, similar_faces=res[:count])
        return SimilarFacesResponse(query_face=query_face, similar_faces=res[:count])
    except ValueError as e:
        print(f"Face ID not found: {face_id}: {e}")
        raise HTTPException(status_code=404, detail="Face ID not found")

@app.get("/face/{face_id}")
async def get_face_image(face_id: str):
    """Serve face image by ID"""
    image_path = FACES_DIR / f"face_{face_id}.jpg"
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

@app.get("/random_component")
async def get_random_component() -> int:
    random_face_id = random.choice(list(face_to_component.keys()))
    comp_id = face_to_component[random_face_id]
    if comp_id in component_people:
        return await get_random_component()
    return comp_id

@app.get("/component/{comp_id}")
async def get_component(comp_id: int):
    photo_sample = random.sample(components[comp_id], min(20, len(components[comp_id])))
    neighbors = []
    if subgraph is not None:
        neighbors = list(subgraph.neighbors(str(comp_id)))
        neighbors = sorted(neighbors, key=lambda x: subgraph.edges[str(comp_id), x]['distance'])
        neighbors = [
            {
                "comp_id": n,
                "size": len(components[int(n)]),
                "sample_face_id": str(random.choice(components[int(n)])),
                "distance": subgraph.edges[str(comp_id), n]['distance']
            }
            for n in neighbors
        ]

    # Add person info if assigned
    person = None
    if comp_id in component_people and component_people[comp_id] in people:
        person = people[component_people[comp_id]]

    return {
        "size": len(components[comp_id]),
        "photos": photo_sample,
        "neighbors": neighbors,
        "person": person
    }

@app.get("/compare-components/{comp_id1}/{comp_id2}")
async def compare_components(comp_id1: str, comp_id2: str, num_pairs: int = 5):
    """Compare two components by finding most similar face pairs between them"""
    # Get faces from both components
    faces1 = components[int(comp_id1)]
    faces2 = components[int(comp_id2)]

    # Get embeddings for faces in both components
    indices1 = [list(face_ids).index(int(face_id)) for face_id in faces1]
    indices2 = [list(face_ids).index(int(face_id)) for face_id in faces2]

    vecs1 = faces[indices1]
    vecs2 = faces[indices2]

    # Calculate cosine distance between all pairs
    distances = 1 - np.dot(vecs1, vecs2.T)

    # Find top pairs
    pairs = []
    for i, j in product(range(len(faces1)), range(len(faces2))):
        dist = float(distances[i][j])
        pairs.append((dist, str(faces1[i]), str(faces2[j])))

    top_pairs = nsmallest(num_pairs, pairs)

    return [{
        "distance": dist,
        "face1_id": face1_id,
        "face2_id": face2_id
    } for dist, face1_id, face2_id in top_pairs]

@app.post("/people")
async def create_person(person: PersonCreate) -> Person:
    """Create a new person"""
    new_id = max(people.keys(), default=0) + 1
    new_person = Person(id=new_id, name=person.name)
    people[new_id] = new_person
    save_people()
    return new_person

@app.get("/people")
async def list_people() -> List[Person]:
    """List all people"""
    return list(people.values())

class PersonSearchResult(BaseModel):
    person: Person
    score: int
    matched_on: str  # 'prefix', 'initials' or 'fuzzy'

@app.get("/people/search", response_model=List[PersonSearchResult])
async def search_people(query: str, limit: int = 10) -> List[PersonSearchResult]:
    """Search people by name with multiple matching strategies"""
    if not query:
        return []

    query = query.lower().strip()
    results: List[Tuple[Person, int, str]] = []
    added_ids = set()

    # 1. Prefix matching (highest priority)
    for person in people.values():
        name_lower = person.name.lower()
        if name_lower.startswith(query):
            results.append((person, 100, 'prefix'))
            added_ids.add(person.id)

    # 2. Initials matching
    if len(query) >= 2:
        initials = ''.join(word[0].lower() for word in query.split())
        for person in people.values():
            person_initials = ''.join(word[0].lower() for word in person.name.split())
            if person_initials.startswith(initials) and person.id not in added_ids:
                results.append((person, 90, 'initials'))
                added_ids.add(person.id)

    # 3. Fuzzy matching (lowest priority)
    if len(results) < limit:
        matches = process.extract(
            query,
            {id: p.name for id, p in people.items()},
            limit=limit,
        )
        for name, score, key in matches:
            if score > 60:
                person = people[key]
                if person.id not in added_ids:  # Avoid duplicates
                    results.append((person, score, 'fuzzy'))
                    added_ids.add(person.id)

    # Sort by score and take top results
    results.sort(key=lambda x: x[1], reverse=True)
    return [
        PersonSearchResult(person=p, score=s, matched_on=m)
        for p, s, m in results[:limit]
    ]

@app.put("/people/{person_id}")
async def update_person(person_id: int, person: PersonCreate) -> Person:
    """Update person name"""
    if person_id not in people:
        raise HTTPException(status_code=404, detail="Person not found")

    people[person_id] = Person(id=person_id, name=person.name)
    save_people()
    return people[person_id]

@app.delete("/people/{person_id}")
async def delete_person(person_id: int):
    """Delete a person"""
    if person_id not in people:
        raise HTTPException(status_code=404, detail="Person not found")

    del people[person_id]
    save_people()
    return {"status": "success"}

@app.put("/component/{comp_id}/person")
async def assign_person_to_component(comp_id: int, data: ComponentPerson):
    """Assign a person to a component"""
    # Validate person exists
    if data.person_id not in people:
        raise HTTPException(status_code=404, detail="Person not found")

    # Validate component exists
    if comp_id >= len(components):
        raise HTTPException(status_code=404, detail="Component not found")

    # Assign person to component
    component_people[comp_id] = data.person_id
    save_component_people()

    return {"status": "success"}

@app.delete("/component/{comp_id}/person")
async def remove_person_from_component(comp_id: int):
    """Remove person assignment from a component"""
    if comp_id in component_people:
        del component_people[comp_id]
        save_component_people()

    return {"status": "success"}

@app.get("/people/{person_id}/components")
async def get_person_components(person_id: int):
    """Get all components assigned to a person"""
    if person_id not in people:
        raise HTTPException(status_code=404, detail="Person not found")

    assigned_components = [
        comp_id for comp_id, pid in component_people.items()
        if pid == person_id
    ]

    return {
        "person": people[person_id],
        "components": [
            {
                "id": comp_id,
                "size": len(components[comp_id]),
                "sample_face_id": str(random.choice(components[comp_id]))
            }
            for comp_id in assigned_components
        ]
    }


@app.get("/propose_subdivision/{comp_id}")
async def propose_subdivision(comp_id: int):
    """Propose subdivision of a component"""
    load_graph()
    subgraph = graph.subgraph([str(i) for i in components[comp_id]])
    subcomponents = nx.community.louvain_communities(subgraph)
    ret = []
    for subcomp in subcomponents:
        ret.append(list(subcomp))

    return {"status": "success", "components": ret}


@app.post("/component/{comp_id}/subdivide")
async def submit_subdivision(comp_id: int, remove_indices: List[int]):
    """Handle subdivision of a component based on user feedback"""
    print(f"submitting subdivision for component {comp_id} with indices {remove_indices}")
    remove_indices = set([str(i) for i in remove_indices])
    src_comp = [i for i in components[comp_id] if i not in remove_indices]
    components[comp_id] = src_comp
    components.append(list(remove_indices))
    with open(settings.subgraph_dir / f"louvain_communities.json", 'w') as f:
        json.dump(components, f, indent=4)
    return {"status": "success", "new_component": len(components)-1}

# Serve index.html as a last resort (on all other paths)
@app.get("/{path:path}")
async def serve_index(path: str):
    return FileResponse(str(settings.static_root / "graphwalk/frontend/dist/index.html"))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
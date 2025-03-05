export const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000';

export interface FaceData {
  image_id: string; // used for fetching context image via /image/{image_id}
  // add other properties if needed
}

export const getFaceImageUrl = (faceId: number) => `${API_BASE}/face/${faceId}`;

export interface FaceWithSimilarity {
    id: number;
    component_id: number;
    person_name: string | null;
    similarity?: number;
}

export interface FaceWithContext extends FaceWithSimilarity {
    face_data: FaceData;
    image_path: string;
    image_date: string | null;
    other_faces: FaceWithSimilarity[];
}

export const getRandomFaces = async (count: number = 20): Promise<FaceWithSimilarity[]> => {
    const response = await fetch(`${API_BASE}/random-faces?count=${count}`);
    if (!response.ok) throw new Error('Failed to fetch random faces');
    return response.json();
};

export interface SimilarFacesResponse {
    query_face: FaceWithSimilarity;
    similar_faces: FaceWithSimilarity[];
}

export const getSimilarFaces = async (faceId: string, count: number = 20, per_bucket: number = 5): Promise<SimilarFacesResponse> => {
    const response = await fetch(`${API_BASE}/similar-faces/${faceId}?count=${count}&per_bucket=${per_bucket}`);
    if (!response.ok) throw new Error('Failed to fetch similar faces');
    return response.json();
};

export interface FacePairComparison {
  distance: number;
  face1_id: number;
  face2_id: number;
}

export const compareComponents = async (comp1Id: number, comp2Id: number): Promise<FacePairComparison[]> => {
  const response = await fetch(`${API_BASE}/compare-components/${comp1Id}/${comp2Id}`);
  if (!response.ok) throw new Error('Failed to compare components');
  return response.json();
};

export const getContextImageUrl = (imageId: string) => `${API_BASE}/image/${imageId}`;

export const getFaceWithContext = async (faceId: string): Promise<FaceWithContext> => {
  const response = await fetch(`${API_BASE}/face_with_context/${faceId}`);
  if (!response.ok) throw new Error('Failed to fetch face with context');
  return response.json();
};
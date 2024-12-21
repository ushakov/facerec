const API_BASE = 'http://localhost:8000';

export const getFaceImageUrl = (faceId: string) => `${API_BASE}/face/${faceId}`;

export interface FaceWithSimilarity {
    id: string;
    component_id: string;
    similarity?: number;
}

export const getRandomFaces = async (count: number = 20): Promise<string[]> => {
    const response = await fetch(`${API_BASE}/random-faces?count=${count}`);
    if (!response.ok) throw new Error('Failed to fetch random faces');
    return response.json();
};

export const getSimilarFaces = async (faceId: string, count: number = 20, per_bucket: number = 5): Promise<FaceWithSimilarity[]> => {
    const response = await fetch(`${API_BASE}/similar-faces/${faceId}?count=${count}&per_bucket=${per_bucket}`);
    if (!response.ok) throw new Error('Failed to fetch similar faces');
    return response.json();
};

interface FacePairComparison {
  distance: number;
  face1_id: string;
  face2_id: string;
}

export const compareComponents = async (comp1Id: string, comp2Id: string): Promise<FacePairComparison[]> => {
  const response = await fetch(`${API_BASE}/compare-components/${comp1Id}/${comp2Id}`);
  if (!response.ok) throw new Error('Failed to compare components');
  return response.json();
};
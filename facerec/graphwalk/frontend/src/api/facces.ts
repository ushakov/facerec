// Add new interface for face data
export interface FaceData {
  image_id: string; // ID used to fetch the context image via /image/{image_id}
  // add other properties if needed
}

// Update FaceWithSimilarity to include the face_data field
export interface FaceWithSimilarity {
  id: number;
  component_id: number | null;
  person_name: string | null;
  similarity: number;
  face_data: FaceData;  // newly added field, reflects backend change
}
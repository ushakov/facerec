import React, { useState, useEffect } from 'react';
import { Face } from './Face';
import { getContextImageUrl, FaceWithSimilarity, FaceWithContext, getFaceWithContext } from '../api/faces';

// Create a type alias extending FaceWithContext to include the optional context_faces property
export type ExtendedFaceWithContext = FaceWithContext & { context_faces?: FaceWithSimilarity[] };

interface ImageContextProps {
  faceId: number;
}

const ImageContext: React.FC<ImageContextProps> = ({ faceId }) => {
  const [loading, setLoading] = useState(true);
  const [face, setFace] = useState<FaceWithContext | null>(null);


  const loadFace = async (faceId: number) => {
    try {
      setLoading(true);
      const faceWithContext = await getFaceWithContext(faceId.toString());
      setFace(faceWithContext);
    } catch (error) {
      console.error('Failed to load similar faces:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadFace(faceId);
  }, [faceId]);

  const contextFaces: FaceWithSimilarity[] = face?.other_faces || [];

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="flex gap-4">
      {/* Left side: main face and context details */}
      <div className="flex flex-col items-center">
        <div className="w-full flex flex-col items-center">
          <img
            src={getContextImageUrl(face?.face_data.image_id || '')}
            alt="Context"
            loading="lazy"
            className="mb-2"
          />
          <div>{face?.image_path}</div>
          {face?.image_date && <div>{face?.image_date}</div>}
        </div>
      </div>

      {/* Right side: grid of other faces from the same context image */}
      <div className="overflow-y-auto  max-w-[500px]">
        <div style={{ display: 'grid', gap: '10px', gridTemplateRows: 'repeat(5, 150px)', gridAutoFlow: 'column', gridAutoColumns: '150px' }}>
          {contextFaces.map((ctxFace: FaceWithSimilarity) => (
            <div key={ctxFace.id} style={{ breakInside: 'avoid', marginBottom: '0.5rem' }} className="w-36 h-36 p-2">
              <Face face={ctxFace} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ImageContext;
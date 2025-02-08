import React from 'react';
import { Face } from './Face';
import { getContextImageUrl, FaceWithSimilarity, FaceWithContext } from '../api/faces';

// Create a type alias extending FaceWithContext to include the optional context_faces property
export type ExtendedFaceWithContext = FaceWithContext & { context_faces?: FaceWithSimilarity[] };

interface ImageContextProps {
  face: ExtendedFaceWithContext;
}

const ImageContext: React.FC<ImageContextProps> = ({ face }) => {
  const contextFaces: FaceWithSimilarity[] = face.other_faces || [];

  return (
    <div className="flex gap-4">
      {/* Left side: main face and context details */}
      <div className="flex flex-col items-center">
        <div className="w-full flex flex-col items-center">
          <img
            src={getContextImageUrl(face.face_data.image_id)}
            alt="Context"
            loading="lazy"
            className="mb-2"
          />
          <div>{face.image_path}</div>
          {face.image_date && <div>{face.image_date}</div>}
        </div>
      </div>

      {/* Right side: grid of other faces from the same context image */}
      <div className="overflow-y-auto h-full">
        <div style={{ columnWidth: '4rem', columnGap: '0.5rem' }} className='flex flex-wrap flex-col'>
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
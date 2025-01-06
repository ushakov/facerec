import { Face } from './Face';
import { Link } from 'react-router-dom';

interface FaceGridProps {
    faceIds: string[];
    selectedFaceId?: string;
    similarities?: Record<string, number>;
    componentIds?: Record<string, string>;
    componentNames?: Record<string, string>;
}

export const FaceGrid: React.FC<FaceGridProps> = ({
    faceIds,
    selectedFaceId,
    similarities,
    componentIds,
    componentNames,
}) => {
    return (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 p-4">
            {faceIds.map((faceId) => (
                <Link key={faceId} to={`/faces/${faceId}`}>
                    <Face
                        faceId={faceId}
                        isSelected={selectedFaceId === faceId}
                        similarity={similarities?.[faceId]}
                        componentId={componentIds?.[faceId]}
                        componentName={componentNames?.[faceId]}
                    />
                </Link>
            ))}
        </div>
    );
};
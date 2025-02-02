import { Face } from './Face';
import { useNavigate } from 'react-router-dom';
import { FaceWithSimilarity } from '../api/faces';

interface FaceGridProps {
    faces: FaceWithSimilarity[];
    selectedFaceId?: number;
}

export const FaceGrid: React.FC<FaceGridProps> = ({
    faces,
    selectedFaceId,
}) => {
    const navigate = useNavigate();

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 p-4">
            {faces.map((face) => (
                <Face
                    key={face.id}
                    face={face}
                    isSelected={selectedFaceId === face.id}
                    onClick={() => navigate(`/faces/${face.id}`)}
                />
            ))}
        </div>
    );
};
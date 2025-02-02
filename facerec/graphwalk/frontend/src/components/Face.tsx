import { motion } from 'framer-motion';
import { Users } from 'lucide-react';
import { FaceWithSimilarity, getFaceImageUrl } from '../api/faces';

interface FaceProps {
    face: FaceWithSimilarity;
    isSelected?: boolean;
    compareLink?: string;
    caption?: React.ReactNode;
    onClick?: () => void;
}

export const Face: React.FC<FaceProps> = ({
    face,
    isSelected,
    compareLink,
    caption,
    onClick,
}) => {
    const componentDisplay = face.person_name || face.component_id;

    return (
        <motion.div
            layoutId={`face-${face.id}`}
            className="relative group w-72 h-72"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            onClick={onClick}
        >
            <motion.div
                className={`
                    cursor-pointer rounded-lg overflow-hidden shadow-lg
                    hover:shadow-xl transition-shadow duration-200
                    ${isSelected ? 'ring-2 ring-primary' : ''}
                `}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
            >
                <img
                    src={getFaceImageUrl(face.id)}
                    alt={`Face ${face.id}`}
                    className="w-full h-full object-cover aspect-square"
                    loading="lazy"
                />
            </motion.div>

            {face.similarity !== undefined && (
                <div className="absolute top-2 right-2 bg-black/50 text-white px-2 py-1 rounded-full text-xs">
                    {face.similarity.toFixed(2)}
                </div>
            )}

            {componentDisplay && (
                <div className="cursor-pointer absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded-full flex flex-row items-center gap-2">
                    <Users size={16} />
                    <span>{componentDisplay}</span>
                </div>
            )}

            {caption && (
                <div className="mt-2 text-sm text-gray-600">
                    {caption}
                </div>
            )}
        </motion.div>
    );
};
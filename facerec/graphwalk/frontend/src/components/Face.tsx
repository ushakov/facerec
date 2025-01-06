import { motion } from 'framer-motion';
import { Users } from 'lucide-react';
import { getFaceImageUrl } from '../api/faces';
import { Link } from 'react-router-dom';

interface FaceProps {
    faceId: string;
    isSelected?: boolean;
    similarity?: number;
    compareLink?: string;
    caption?: React.ReactNode;
    componentId?: string;
    componentName?: string;
}

export const Face: React.FC<FaceProps> = ({
    faceId,
    isSelected,
    similarity,
    compareLink,
    caption,
    componentId,
    componentName,
}) => {
    const componentDisplay = componentName || `${componentId}`;
    const componentLink = componentId ? `/components/${componentId}` : undefined;
    return (
        <motion.div
            layoutId={`face-${faceId}`}
            className="relative group"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
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
                    src={getFaceImageUrl(faceId)}
                    alt={`Face ${faceId}`}
                    className="w-full h-full object-cover aspect-square"
                    loading="lazy"
                />
            </motion.div>

            {similarity !== undefined && (
                <div className="absolute top-2 right-2 bg-black/50 text-white px-2 py-1 rounded-full text-xs">
                    {similarity.toFixed(2)}
                </div>
            )}

            {componentLink && (
                <Link
                    to={componentLink}
                    className="absolute bottom-2 right-2 bg-black/50 hover:bg-black/70 text-white p-1.5 rounded-full flex flex-row items-center gap-2"
                    title="View cluster"
                >
                    <Users size={16} /> {componentDisplay}
                </Link>
            )}

            {compareLink && (
                <Link
                    to={compareLink}
                    className="absolute top-2 right-2 bg-black/50 text-white px-2 py-1 rounded-full text-xs
                             opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => e.stopPropagation()}
                >
                    Compare
                </Link>
            )}

            {caption && (
                <div className="mt-2 text-sm">
                    {caption}
                </div>
            )}
        </motion.div>
    );
};
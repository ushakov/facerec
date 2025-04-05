import React from 'react';
import { TimelineFace as TimelineFaceType } from '../api/faces';
import { formatShortDate } from '../utils/dates';
import { getFaceImageUrl } from '../api/faces';

interface TimelineFaceProps {
    face: TimelineFaceType;
    onClick?: () => void;
}

export const TimelineFace: React.FC<TimelineFaceProps> = ({ face, onClick }) => {
    return (
        <div
            className="group relative w-72 h-72 cursor-pointer transition-transform hover:scale-105"
            onClick={onClick}
        >
            <img
                src={getFaceImageUrl(face.face_id)}
                alt={`Face from ${face.image_date || 'unknown date'}`}
                className="w-full h-full object-cover rounded-lg shadow-sm"
                loading="lazy"
            />
            <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 rounded-b-lg">
                {formatShortDate(face.image_date)}
            </div>

            {/* Hover overlay with full resolution preview */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity rounded-lg">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                    Click to view
                </div>
            </div>
        </div>
    );
};
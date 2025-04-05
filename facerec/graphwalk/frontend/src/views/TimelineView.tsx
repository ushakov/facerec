import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TimelineFace as TimelineFaceType, getPersonTimeline } from '../api/faces';
import { TimelineFace } from '../components/TimelineFace';
import { groupTimelineFaces } from '../utils/dates';
import ImageContext from '../components/ImageContext';

export const TimelineView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [faces, setFaces] = useState<TimelineFaceType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedFace, setSelectedFace] = useState<number | null>(null);

  const observer = useRef<IntersectionObserver>();
  const lastFaceElementRef = useCallback((node: HTMLDivElement | null) => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1);
      }
    });
    if (node) observer.current.observe(node);
  }, [loading, hasMore]);

  const loadFaces = useCallback(async (pageNum: number) => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      const response = await getPersonTimeline(parseInt(id), pageNum, 20, sortOrder);
      setFaces(prev => pageNum === 1 ? response.faces : [...prev, ...response.faces]);
      setHasMore(response.has_more);
    } catch (err) {
      setError('Failed to load timeline faces');
      console.error('Error loading timeline:', err);
    } finally {
      setLoading(false);
    }
  }, [id, sortOrder]);

  useEffect(() => {
    setPage(1);
    setFaces([]);
    loadFaces(1);
  }, [id, sortOrder, loadFaces]);

  useEffect(() => {
    if (page > 1) {
      loadFaces(page);
    }
  }, [page, loadFaces]);

  const groupedFaces = groupTimelineFaces(faces);
  const years = Object.keys(groupedFaces).sort((a, b) =>
    sortOrder === 'desc' ? b.localeCompare(a) : a.localeCompare(b)
  );

  return (
    <div className="p-4 max-w-7xl mx-auto">
      {/* Header with sorting controls */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Timeline View</h1>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2">
            <span className="text-sm font-medium">Sort order:</span>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
              className="rounded border p-1"
            >
              <option value="desc">Newest first</option>
              <option value="asc">Oldest first</option>
            </select>
          </label>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Timeline content */}
      <div className="space-y-8">
        {years.map((year) => (
          <div key={year} className="space-y-6">
            <h2 className="text-xl font-semibold sticky top-0 bg-white py-2 z-10 border-b">
              {year}
            </h2>
            {Object.entries(groupedFaces[year]).map(([month, monthFaces]) => (
              <div key={month} className="space-y-4">
                <h3 className="text-lg font-medium text-gray-600">{month}</h3>
                <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {monthFaces.map((face, index) => (
                    <div
                      key={`${face.face_id}-${face.image_date}`}
                      ref={index === monthFaces.length - 1 ? lastFaceElementRef : undefined}
                    >
                      <TimelineFace
                        face={face}
                        onClick={() => setSelectedFace(face.face_id)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      {loading && (
        <div className="flex justify-center my-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      )}

      {/* Modal for showing face context */}
      {selectedFace && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-4">
              <button
                onClick={() => setSelectedFace(null)}
                className="float-right text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
              <ImageContext faceId={selectedFace} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
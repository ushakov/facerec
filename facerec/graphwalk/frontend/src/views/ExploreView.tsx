import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { FaceGrid } from '../components/FaceGrid';
import { getRandomFaces, getSimilarFaces, FaceWithSimilarity } from '../api/faces';
import { useParams } from 'react-router-dom';
import { Face } from '../components/Face';

export function ExploreView() {
  const { id } = useParams();
  const [faces, setFaces] = useState<FaceWithSimilarity[]>([]);
  const [selectedFace, setSelectedFace] = useState<FaceWithSimilarity | null>(null);
  const [similarFaces, setSimilarFaces] = useState<FaceWithSimilarity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const handleFaceClick = useCallback(async (faceId: string) => {
    try {
      setIsLoading(true);
      const response = await getSimilarFaces(faceId);
      setSimilarFaces(response.similar_faces);
      setSelectedFace(response.query_face);
    } catch (error) {
      console.error('Failed to load similar faces:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    async function load() {
        if (id) {
            handleFaceClick(id);
        } else {
            loadRandomFaces();
        }
    }
    load();
  }, [id, handleFaceClick]);

  const loadRandomFaces = async () => {
    try {
      setIsLoading(true);
      const faces = await getRandomFaces(20);
      setFaces(faces);
      setSelectedFace(null);
    } catch (error) {
      console.error('Failed to load random faces:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-base-200">
      <header className="bg-base-100 shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary">Face Explorer</h1>
            <button
              onClick={loadRandomFaces}
              className="btn btn-primary"
              disabled={isLoading}
            >
              Shuffle Faces
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto py-8">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex justify-center items-center h-64"
            >
              <div className="loading loading-spinner loading-lg text-primary"></div>
            </motion.div>
          ) : (
            <motion.div
              key="content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {selectedFace ? (
                <>
                  <div className="flex justify-center mb-8">
                    <Face face={selectedFace} />
                  </div>
                  <h2 className="text-xl font-semibold text-center mb-4">Similar Faces</h2>
                  <FaceGrid faces={similarFaces} selectedFaceId={selectedFace.id} />
                </>
              ) : (
                <FaceGrid faces={faces} />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
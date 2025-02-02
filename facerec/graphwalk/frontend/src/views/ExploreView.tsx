import { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { FaceGrid } from '../components/FaceGrid';
import { getRandomFaces, getSimilarFaces, getFaceImageUrl, FaceWithSimilarity } from '../api/faces';
import { useParams } from 'react-router-dom';

export function ExploreView() {
  const { id } = useParams();
  const [faceIds, setFaceIds] = useState<string[]>([]);
  const [selectedFaceId, setSelectedFaceId] = useState<string | null>(null);
  const [similarFaces, setSimilarFaces] = useState<FaceWithSimilarity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
        if (id) {
            handleFaceClick(id);
        } else {
            loadRandomFaces();
        }
    }
    load();
  }, [id]);

  const loadRandomFaces = async () => {
    try {
      setIsLoading(true);
      const faces = await getRandomFaces(20);
      setSelectedFaceId(null);
      setFaceIds(faces);
    } catch (error) {
      console.error('Failed to load random faces:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFaceClick = async (faceId: string) => {
    try {
      setIsLoading(true);
      setSelectedFaceId(faceId);
      const similar = await getSimilarFaces(faceId);
      setSimilarFaces(similar);
    } catch (error) {
      console.error('Failed to load similar faces:', error);
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
              {selectedFaceId ? (
                <>
                  <div className="flex justify-center mb-8">
                    <motion.div
                      layoutId={`face-${selectedFaceId}`}
                      className="w-64 h-64 rounded-lg overflow-hidden shadow-xl"
                    >
                      <img
                        src={getFaceImageUrl(selectedFaceId)}
                        alt={`Face ${selectedFaceId}`}
                        className="w-full h-full object-cover"
                      />
                    </motion.div>
                  </div>
                  <h2 className="text-xl font-semibold text-center mb-4">Similar Faces</h2>
                  <FaceGrid
                    faceIds={similarFaces.map(face => face.id)}
                    similarities={Object.fromEntries(similarFaces.map(face => [face.id, face.similarity ?? 0]))}
                    componentIds={Object.fromEntries(similarFaces.map(face => [face.id, face.person_name ?? face.component_id]))}
                    selectedFaceId={selectedFaceId}
                  />
                </>
              ) : (
                <FaceGrid
                  faceIds={faceIds}
                  selectedFaceId={selectedFaceId ?? undefined}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
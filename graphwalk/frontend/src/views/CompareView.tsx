import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { compareComponents } from '../api/faces';
import { getFaceImageUrl } from '../api/faces';

interface FacePair {
  distance: number;
  face1_id: string;
  face2_id: string;
}

export function CompareView() {
  const [pairs, setPairs] = useState<FacePair[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { id1, id2 } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    if (!id1 || !id2) return;

    const loadComparison = async () => {
      try {
        setIsLoading(true);
        const data = await compareComponents(id1, id2);
        setPairs(data);
      } catch (error) {
        console.error('Failed to compare components:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadComparison();
  }, [id1, id2]);

  return (
    <div className="min-h-screen bg-base-200">
      <header className="bg-base-100 shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary">Component Comparison</h1>
            <button
              onClick={() => navigate(`/components/${id1}`)}
              className="btn btn-primary"
            >
              Back to Component
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
              className="grid gap-8"
            >
              {pairs.map((pair, idx) => (
                <motion.div
                  key={idx}
                  className="card bg-base-100 shadow-xl"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <div className="card-body">
                    <h2 className="card-title">Distance: {pair.distance.toFixed(3)}</h2>
                    <div className="flex justify-center gap-4">
                      <div className="w-64 h-64">
                        <img
                          src={getFaceImageUrl(pair.face1_id)}
                          alt={`Face ${pair.face1_id}`}
                          className="w-full h-full object-cover rounded-lg"
                        />
                      </div>
                      <div className="w-64 h-64">
                        <img
                          src={getFaceImageUrl(pair.face2_id)}
                          alt={`Face ${pair.face2_id}`}
                          className="w-full h-full object-cover rounded-lg"
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
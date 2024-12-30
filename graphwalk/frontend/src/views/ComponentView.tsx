import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { RefreshCcw } from 'lucide-react';
import { FaceGrid } from '../components/FaceGrid';
import { Face } from '../components/Face';
import { PersonSearchOrAdd } from '../components/PersonSearchOrAdd';
import { User, UserPlus } from 'lucide-react';

interface Neighbor {
  comp_id: string;
  sample_face_id: string;
  distance: number;
  size: number;
}

interface Person {
  id: number;
  name: string;
}

interface ComponentData {
  photos: string[];
  neighbors: Neighbor[];
  size: number;
  person?: Person;
}

export function ComponentView() {
  const [componentData, setComponentData] = useState<ComponentData>({ photos: [], neighbors: [], size: 0 });
  const [componentId, setComponentId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const { id } = useParams();
  const navigate = useNavigate();
  const [isAssigningPerson, setIsAssigningPerson] = useState(false);

  const loadComponent = async (compId: string) => {
    try {
      setIsLoading(true);
      setComponentId(compId);
      const response = await fetch(`http://localhost:8000/component/${compId}`);
      const data = await response.json();
      setComponentData(data);
    } catch (error) {
      console.error('Failed to load component:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRandomComponent = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/random_component');
      const compId = await response.text();
      navigate(`/components/${compId}`);
    } catch (error) {
      console.error('Failed to load random component:', error);
    }
  };

  const reloadComponent = () => {
    if (componentId) {
      loadComponent(componentId);
    }
  };

  const handlePersonSelect = async (person: Person) => {
    try {
      await fetch(`http://localhost:8000/component/${componentId}/person`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ person_id: person.id }),
      });
      reloadComponent();
      setIsAssigningPerson(false);
    } catch (error) {
      console.error('Failed to assign person:', error);
    }
  };

  useEffect(() => {
    if (id) {
      loadComponent(id);
    } else {
      loadRandomComponent();
    }
  }, [id]);

  return (
    <div className="min-h-screen bg-base-200">
      <header className="bg-base-100 shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-primary">
                Component #{componentId} ({componentData.size} photos)
              </h1>
              {componentData.person ? (
                <div className="flex items-center gap-2 bg-base-100 px-3 py-1 rounded-full">
                  <User className="w-4 h-4" />
                  <span>{componentData.person.name}</span>
                  <button
                    className="btn btn-ghost btn-xs"
                    onClick={() => setIsAssigningPerson(true)}
                  >
                    Edit
                  </button>
                </div>
              ) : (
                <button
                  className="btn btn-outline btn-sm gap-2"
                  onClick={() => setIsAssigningPerson(true)}
                >
                  <UserPlus className="w-4 h-4" />
                  Assign Person
                </button>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={reloadComponent}
                className="btn btn-secondary"
                disabled={isLoading}
              >
                <RefreshCcw className="w-4 h-4" />
              </button>
              <button
                onClick={loadRandomComponent}
                className="btn btn-primary"
                disabled={isLoading}
              >
                Load Random Component
              </button>
            </div>
          </div>
        </div>
      </header>

      {isAssigningPerson && (
        <PersonSearchOrAdd
          onSelect={handlePersonSelect}
          onClose={() => setIsAssigningPerson(false)}
        />
      )}

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
              className="space-y-8"
            >
              <div>
                <h2 className="text-xl font-semibold mb-4">Photos in Component</h2>
                <FaceGrid
                  faceIds={componentData.photos}
                />
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-4">Similar Components</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {componentData.neighbors.map((neighbor) => (
                    <Face
                      key={neighbor.comp_id}
                      faceId={neighbor.sample_face_id}
                      compareLink={`/compare/${componentId}/${neighbor.comp_id}`}
                      componentId={neighbor.comp_id}
                      caption={
                        <>
                          Component #{neighbor.comp_id} ({neighbor.size} photos)
                          <br />
                          Distance: {neighbor.distance.toFixed(2)}
                        </>
                      }
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { RefreshCcw, X, User, UserPlus, GitBranch } from 'lucide-react';
import { FaceGrid } from '../components/FaceGrid';
import { Face } from '../components/Face';
import { PersonSearchOrAdd } from '../components/PersonSearchOrAdd';
import { FaceWithSimilarity, API_BASE } from '../api/faces';

interface Neighbor {
  comp_id: number;
  sample_face_id: number;
  distance: number;
  size: number;
}

interface Person {
  id: number;
  name: string;
}

interface ComponentData {
  photos: number[];
  neighbors: Neighbor[];
  size: number;
  person?: Person;
}

interface SubdivisionProposal {
  components: number[][];
}

export function ComponentView() {
  const [componentData, setComponentData] = useState<ComponentData>({ photos: [], neighbors: [], size: 0 });
  const [componentId, setComponentId] = useState<number>(-1);
  const [isLoading, setIsLoading] = useState(true);
  const [subdivisionProposal, setSubdivisionProposal] = useState<SubdivisionProposal | null>(null);
  const [isShowingSubdivisions, setIsShowingSubdivisions] = useState(false);
  const { id } = useParams();
  const navigate = useNavigate();
  const [isAssigningPerson, setIsAssigningPerson] = useState(false);
  const [differentPersonIndices, setDifferentPersonIndices] = useState<number[]>([]);

  const loadComponent = async (compId: number) => {
    try {
      setIsLoading(true);
      setComponentId(compId);
      const response = await fetch(`${API_BASE}/component/${compId}`);
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
      const response = await fetch(`${API_BASE}/random_component`);
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
      await fetch(`${API_BASE}/component/${componentId}/person`, {
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

  const proposeSubdivision = async () => {
    try {
      const response = await fetch(`${API_BASE}/propose_subdivision/${componentId}`);
      const data = await response.json();
      setSubdivisionProposal(data);
      setIsShowingSubdivisions(true);
    } catch (error) {
      console.error('Failed to propose subdivision:', error);
    }
  };

  const handleSubdivisionSubmit = async () => {
    if (!subdivisionProposal) {
      return;
    }
    const submit_data: number[] = [];
    for (let i = 0; i < differentPersonIndices.length; i++) {
      const comp = subdivisionProposal.components[differentPersonIndices[i]];
      for (let j = 0; j < comp.length; j++) {
        submit_data.push(comp[j]);
      }
    }
    try {
      const response = await fetch(`${API_BASE}/component/${componentId}/subdivide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submit_data),
      });
      const data = await response.json();
      if (data.status === 'success') {
        setComponentId(data.new_component);
        navigate(`/components/${componentId}`);
      }
    } catch (error) {
      console.error('Failed to submit subdivision:', error);
    }
  };

  useEffect(() => {
    if (id && !isNaN(parseInt(id, 10))) {
      loadComponent(parseInt(id, 10));
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
              <button
                onClick={proposeSubdivision}
                className="btn btn-info btn-sm gap-2"
              >
                <GitBranch className="w-4 h-4" />
                Propose Subdivision
              </button>
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

      {isShowingSubdivisions && subdivisionProposal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-base-100 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Proposed Subdivisions</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setSubdivisionProposal({...subdivisionProposal})}
                  className="btn btn-ghost btn-sm"
                >
                  <RefreshCcw className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setIsShowingSubdivisions(false)}
                  className="btn btn-ghost btn-sm"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div className="space-y-8">
              {subdivisionProposal.components.map((subcomponent, index) => {
                const randomPhotos = subcomponent
                  .sort(() => Math.random() - 0.5)
                  .slice(0, 20);

                const facesData: FaceWithSimilarity[] = randomPhotos.map(id => ({
                  id,
                  component_id: componentId,
                  person_name: componentData.person?.name || null,
                }));

                return (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center gap-4">
                      <h3 className="text-lg font-semibold">
                        Subcomponent {index + 1} ({subcomponent.length} photos)
                      </h3>
                      <label className="label cursor-pointer">
                        <input
                          type="checkbox"
                          className="checkbox checkbox-primary"
                          checked={differentPersonIndices.includes(index)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setDifferentPersonIndices([...differentPersonIndices, index]);
                            } else {
                              setDifferentPersonIndices(
                                differentPersonIndices.filter((i) => i !== index)
                              );
                            }
                          }}
                        />
                        <span className="label-text ml-2">Different Person</span>
                      </label>
                    </div>
                    <FaceGrid faces={facesData} />
                  </div>
                );
              })}
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button
                onClick={() => {
                  setIsShowingSubdivisions(false);
                  setDifferentPersonIndices([]);
                }}
                className="btn btn-ghost"
              >
                Cancel
              </button>
              <button
                onClick={handleSubdivisionSubmit}
                className="btn btn-primary"
                disabled={differentPersonIndices.length === 0}
              >
                Submit Subdivisions
              </button>
            </div>
          </div>
        </div>
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
                  faces={componentData.photos.map(id => ({
                    id,
                    component_id: componentId,
                    person_name: componentData.person?.name || null,
                  }))}
                />
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-4">Similar Components</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {componentData.neighbors.map((neighbor) => (
                    <Face
                      key={neighbor.comp_id}
                      face={{
                        id: neighbor.sample_face_id,
                        component_id: neighbor.comp_id,
                        person_name: null,
                        similarity: neighbor.distance,
                      }}
                      onClick={() => navigate(`/components/${neighbor.comp_id}`)}
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
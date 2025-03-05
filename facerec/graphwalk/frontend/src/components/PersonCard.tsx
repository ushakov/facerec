import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronRight, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Face } from './Face';
import { FaceWithSimilarity, API_BASE } from '../api/faces';

interface Person {
  id: number;
  name: string;
}

interface Component {
  id: number;
  size: number;
  sample_face_id: number;
}

interface PersonCardProps {
  person: Person;
  onDelete: (id: number) => Promise<void>;
}

export function PersonCard({ person, onDelete }: PersonCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [components, setComponents] = useState<Component[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const loadComponents = async () => {
    if (components.length > 0 || isLoading) return;

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE}/people/${person.id}/components`);
      const data = await response.json();
      setComponents(data.components);
    } catch (error) {
      console.error('Failed to load person components:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = () => {
    if (!isExpanded) {
      loadComponents();
    }
    setIsExpanded(!isExpanded);
  };

  const componentToFace = (component: Component): FaceWithSimilarity => ({
    id: component.sample_face_id,
    component_id: component.id,
    person_name: person.name,
    similarity: 0
  });

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="card bg-base-100 shadow-lg"
    >
      <div className="card-body p-4">
        <div className="flex justify-between items-center">
          <button
            className="flex items-center gap-2 flex-1"
            onClick={handleToggle}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <h2 className="card-title m-0">{person.name}</h2>
          </button>
          <button
            onClick={() => onDelete(person.id)}
            className="btn btn-ghost btn-sm text-error"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 overflow-hidden"
            >
              {isLoading ? (
                <div className="flex justify-center py-4">
                  <div className="loading loading-spinner loading-sm"></div>
                </div>
              ) : components.length ? (
                <div className="grid grid-cols-3 gap-2">
                  {components.map(component => (
                    <div key={component.id} className="w-60 h-72 p-2">
                      <Face
                          key={component.id}
                          face={componentToFace(component)}
                          onClick={() => navigate(`/components/${component.id}`)}
                          caption={
                          <div className="text-center text-xs text-base-content/70">
                            {component.size} faces
                          </div>
                          }
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4 text-base-content/50">
                  No face clusters assigned
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
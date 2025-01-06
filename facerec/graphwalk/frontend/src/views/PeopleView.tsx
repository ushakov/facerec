import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, RefreshCcw } from 'lucide-react';
import { PersonSearchDropdown } from '../components/PersonSearchDropdown';

interface Person {
  id: number;
  name: string;
}

export function PeopleView() {
  const [people, setPeople] = useState<Person[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newPersonName, setNewPersonName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const loadPeople = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/people');
      const data = await response.json();
      setPeople(data);
    } catch (error) {
      console.error('Failed to load people:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPeople();
  }, []);

  const handleCreatePerson = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPersonName.trim()) return;

    try {
      const response = await fetch('http://localhost:8000/people', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newPersonName.trim() })
      });
      const newPerson = await response.json();
      setPeople([...people, newPerson]);
      setNewPersonName('');
      setIsCreating(false);
    } catch (error) {
      console.error('Failed to create person:', error);
    }
  };

  const handleDeletePerson = async (id: number) => {
    try {
      await fetch(`http://localhost:8000/people/${id}`, { method: 'DELETE' });
      setPeople(people.filter(p => p.id !== id));
    } catch (error) {
      console.error('Failed to delete person:', error);
    }
  };

  return (
    <div className="min-h-screen bg-base-200">
      <header className="bg-base-100 shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary">People</h1>
            <div className="flex gap-2">
              <button
                onClick={() => loadPeople()}
                className="btn btn-secondary"
                disabled={isLoading}
              >
                <RefreshCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsCreating(true)}
                className="btn btn-primary"
                disabled={isLoading}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Person
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto py-8">
        <div className="mb-8 max-w-xl mx-auto">
          <PersonSearchDropdown
            onSelect={(person) => console.log('Selected:', person)}
            placeholder="Search people..."
            className="w-full"
          />
        </div>

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
              className="grid gap-4 max-w-xl mx-auto"
            >
              {isCreating && (
                <motion.form
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="card bg-base-100 shadow-lg"
                  onSubmit={handleCreatePerson}
                >
                  <div className="card-body">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newPersonName}
                        onChange={(e) => setNewPersonName(e.target.value)}
                        placeholder="Enter person name..."
                        className="input input-bordered flex-1"
                        autoFocus
                      />
                      <button type="submit" className="btn btn-primary">Add</button>
                      <button
                        type="button"
                        className="btn btn-ghost"
                        onClick={() => setIsCreating(false)}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </motion.form>
              )}

              {people.map((person) => (
                <motion.div
                  key={person.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="card bg-base-100 shadow-lg"
                >
                  <div className="card-body py-4 flex-row justify-between items-center">
                    <h2 className="card-title m-0">{person.name}</h2>
                    <button
                      onClick={() => handleDeletePerson(person.id)}
                      className="btn btn-ghost btn-sm text-error"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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
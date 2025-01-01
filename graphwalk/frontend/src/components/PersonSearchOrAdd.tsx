import { useState, useEffect, useRef } from 'react';
import { Search, Plus } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Person {
  id: number;
  name: string;
}

interface PersonSearchResult {
  person: Person;
  score: number;
  matched_on: 'prefix' | 'initials' | 'fuzzy';
}

interface PersonSearchOrAddProps {
  onSelect: (person: Person) => void;
  onClose: () => void;
  className?: string;
}

export function PersonSearchOrAdd({ onSelect, onClose, className = '' }: PersonSearchOrAddProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PersonSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const searchPeople = async () => {
      if (!query.trim()) {
        setResults([]);
        return;
      }

      try {
        setIsLoading(true);
        const response = await fetch(`http://localhost:8000/people/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        setResults(data);
      } catch (error) {
        console.error('Failed to search people:', error);
      } finally {
        setIsLoading(false);
      }
    };

    const timeoutId = setTimeout(searchPeople, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleCreatePerson = async () => {
    if (!query.trim()) return;

    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/people', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: query }),
      });
      const person = await response.json();
      onSelect(person);
    } catch (error) {
      console.error('Failed to create person:', error);
    }
  };

  const getHighlightedName = (name: string, matchedOn: string) => {
    if (matchedOn === 'prefix' && query) {
      const index = name.toLowerCase().indexOf(query.toLowerCase());
      if (index >= 0) {
        return (
          <>
            {name.slice(0, index)}
            <span className="bg-primary/20">{name.slice(index, index + query.length)}</span>
            {name.slice(index + query.length)}
          </>
        );
      }
    }
    return name;
  };

  return (
    <div className="modal modal-open">
      <div className="modal-box" ref={dropdownRef}>
        <h3 className="font-bold text-lg mb-4">Search or Add Person</h3>

        <div className="relative mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search or enter new name..."
            className="input input-bordered w-full pr-10"
            autoFocus
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            {isLoading ? (
              <div className="loading loading-spinner loading-sm text-primary"></div>
            ) : (
              <Search className="w-5 h-5 text-base-content/50" />
            )}
          </div>
        </div>

        <AnimatePresence>
          {results.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="mb-4"
            >
              <div className="text-sm text-base-content/60 mb-2">Existing matches:</div>
              <ul className="space-y-1">
                {results.map((result) => (
                  <li
                    key={result.person.id}
                    onClick={() => onSelect(result.person)}
                    className="p-2 hover:bg-base-200 rounded-lg cursor-pointer"
                  >
                    <div className="font-medium">
                      {getHighlightedName(result.person.name, result.matched_on)}
                    </div>
                  </li>
                ))}
              </ul>
            </motion.div>
          )}
        </AnimatePresence>

        {query.trim() && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mb-4"
          >
            <div className="divider">or</div>
            <button
              className="btn btn-primary w-full gap-2"
              onClick={handleCreatePerson}
            >
              <Plus className="w-4 h-4" />
              Create new person "{query}"
            </button>
          </motion.div>
        )}

        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
      <div className="modal-backdrop" onClick={onClose} />
    </div>
  );
}
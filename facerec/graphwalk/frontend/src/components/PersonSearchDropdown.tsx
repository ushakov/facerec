import { useState, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE } from '../api/faces';

interface Person {
  id: number;
  name: string;
}

interface PersonSearchResult {
  person: Person;
  score: number;
  matched_on: 'prefix' | 'initials' | 'fuzzy';
}

interface PersonSearchDropdownProps {
  onSelect: (person: Person) => void;
  placeholder?: string;
  className?: string;
}

export function PersonSearchDropdown({ onSelect, placeholder = 'Search people...', className = '' }: PersonSearchDropdownProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PersonSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const searchPeople = async () => {
      if (!query.trim()) {
        setResults([]);
        return;
      }

      try {
        setIsLoading(true);
        const response = await fetch(`${API_BASE}/people/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        setResults(data);
        setIsOpen(true);
      } catch (error) {
        console.error('Failed to search people:', error);
      } finally {
        setIsLoading(false);
      }
    };

    const timeoutId = setTimeout(searchPeople, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSelect = (result: PersonSearchResult) => {
    onSelect(result.person);
    setQuery('');
    setIsOpen(false);
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
    <div className={`relative ${className}`} ref={dropdownRef}>
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="input input-bordered w-full pr-10"
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
        {isOpen && results.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 w-full mt-1 bg-base-100 rounded-lg shadow-lg overflow-hidden"
          >
            <ul className="py-1">
              {results.map((result) => (
                <motion.li
                  key={result.person.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="px-4 py-2 hover:bg-base-200 cursor-pointer"
                  onClick={() => handleSelect(result)}
                >
                  <div className="font-medium">
                    {getHighlightedName(result.person.name, result.matched_on)}
                  </div>
                  <div className="text-xs text-base-content/60">
                    {result.matched_on === 'prefix' ? 'Starts with' :
                     result.matched_on === 'initials' ? 'Matches initials' :
                     `${result.score}% match`}
                  </div>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
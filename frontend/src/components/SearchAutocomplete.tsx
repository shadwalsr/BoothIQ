import React, { useState, useEffect, useRef } from 'react';

interface ConstituencyItem {
  id: number;
  name: string;
  district: string;
  cluster_id: number | null;
}

interface SearchAutocompleteProps {
  constituencies: ConstituencyItem[];
  onSelect: (id: number) => void;
  activeId: number | null;
}

// Levenshtein string distance helper to support fuzzy search recommendations (AC7)
const getLevenshteinDistance = (a: string, b: string): number => {
  const tmp: number[][] = [];
  for (let i = 0; i <= a.length; i++) {
    tmp[i] = [i];
  }
  for (let j = 0; j <= b.length; j++) {
    tmp[0][j] = j;
  }
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      tmp[i][j] = Math.min(
        tmp[i - 1][j] + 1, // deletion
        tmp[i][j - 1] + 1, // insertion
        tmp[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1) // substitution
      );
    }
  }
  return tmp[a.length][b.length];
};

export const SearchAutocomplete: React.FC<SearchAutocompleteProps> = ({
  constituencies,
  onSelect,
  activeId,
}) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync active constituency to input field on load or select
  useEffect(() => {
    if (activeId !== null) {
      const active = constituencies.find((c) => c.id === activeId);
      if (active) {
        setQuery(`${active.name} (AC #${active.id})`);
      }
    } else {
      setQuery('');
    }
  }, [activeId, constituencies]);

  // 1. Filter list based on search term (substring matching)
  const filtered = query
    ? constituencies.filter(
        (c) =>
          c.name.toLowerCase().includes(query.toLowerCase()) ||
          c.district.toLowerCase().includes(query.toLowerCase()) ||
          c.id.toString() === query.trim()
      )
    : constituencies;

  // 2. Calculate fuzzy suggestions if there are zero substring matches (AC7)
  const showFuzzy = query && filtered.length === 0;
  const fuzzySuggestions = showFuzzy
    ? [...constituencies]
        .map((c) => {
          const nameDist = getLevenshteinDistance(query.toLowerCase(), c.name.toLowerCase());
          const maxLen = Math.max(query.length, c.name.length);
          const score = 1 - nameDist / maxLen;
          return { item: c, score };
        })
        .filter((x) => x.score > 0.35) // threshold score to ignore completely off matches
        .sort((a, b) => b.score - a.score)
        .slice(0, 4) // Limit top suggestions
        .map((x) => x.item)
    : [];

  const itemsToRender = showFuzzy ? fuzzySuggestions : filtered;

  // Handle outside clicks to close dropdown
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1) % Math.max(1, itemsToRender.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev - 1 + itemsToRender.length) % Math.max(1, itemsToRender.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (highlightedIndex >= 0 && highlightedIndex < itemsToRender.length) {
        selectItem(itemsToRender[highlightedIndex]);
      } else if (itemsToRender.length > 0) {
        selectItem(itemsToRender[0]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const selectItem = (item: ConstituencyItem) => {
    onSelect(item.id);
    setQuery(`${item.name} (AC #${item.id})`);
    setIsOpen(false);
    setHighlightedIndex(-1);
    if (inputRef.current) {
      inputRef.current.blur();
    }
  };

  return (
    <div className="search-container" ref={dropdownRef}>
      <div className="search-input-wrapper">
        <span className="search-icon">🔍</span>
        <input
          ref={inputRef}
          type="text"
          placeholder="Search constituency name, district, or ID..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
            setHighlightedIndex(0);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          className="search-input"
        />
        {query && (
          <button
            type="button"
            className="clear-btn"
            onClick={() => {
              setQuery('');
              setIsOpen(true);
              if (inputRef.current) inputRef.current.focus();
            }}
          >
            ✕
          </button>
        )}
      </div>

      {isOpen && (
        <div className="search-dropdown glass-panel animate-fade-in">
          {itemsToRender.length === 0 ? (
            <div className="no-results">No constituencies found</div>
          ) : (
            <div className="dropdown-scroll-wrapper">
              {showFuzzy && (
                <div className="fuzzy-header">Did you mean?</div>
              )}
              {itemsToRender.map((item, idx) => {
                const isSelected = item.id === activeId;
                const isHighlighted = idx === highlightedIndex;
                return (
                  <div
                    key={item.id}
                    onClick={() => selectItem(item)}
                    onMouseEnter={() => setHighlightedIndex(idx)}
                    className={`dropdown-item ${isSelected ? 'selected' : ''} ${
                      isHighlighted ? 'highlighted' : ''
                    }`}
                  >
                    <div className="item-name">
                      {item.name} <span className="item-ac">AC #{item.id}</span>
                    </div>
                    <div className="item-district">{item.district} District</div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      <style>{`
        .search-container {
          position: relative;
          width: 100%;
          max-width: 600px;
          margin: 0 auto 2.5rem;
          z-index: 100;
        }
        .search-input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
          background: rgba(22, 26, 43, 0.8);
          border: 1px solid var(--border-color);
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-md);
          transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
        }
        .search-input-wrapper:focus-within {
          border-color: var(--color-primary);
          box-shadow: 0 0 15px rgba(99, 102, 241, 0.25);
        }
        .search-icon {
          padding-left: 1rem;
          color: var(--text-muted);
          font-size: 1.1rem;
        }
        .search-input {
          width: 100%;
          background: transparent;
          border: none;
          outline: none;
          color: var(--text-primary);
          font-family: var(--font-sans);
          font-size: 1rem;
          padding: 1rem 0.75rem;
        }
        .clear-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          font-size: 0.9rem;
          padding: 0.5rem 1rem;
          transition: color var(--transition-fast);
        }
        .clear-btn:hover {
          color: var(--text-primary);
        }
        .search-dropdown {
          position: absolute;
          top: calc(100% + 0.5rem);
          left: 0;
          right: 0;
          max-height: 350px;
          overflow-y: auto;
          z-index: 101;
          border: 1px solid var(--border-color-hover);
          background: rgba(10, 11, 16, 0.95);
          box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
        }
        .dropdown-scroll-wrapper {
          padding: 0.5rem;
        }
        .fuzzy-header {
          padding: 0.5rem 1rem 0.25rem;
          font-family: var(--font-heading);
          font-size: 0.75rem;
          font-weight: 700;
          color: var(--warning);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-bottom: 1px solid rgba(255, 255, 255, 0.05);
          margin-bottom: 0.5rem;
        }
        .dropdown-item {
          padding: 0.75rem 1rem;
          border-radius: var(--radius-sm);
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
          transition: background var(--transition-fast);
          margin-bottom: 2px;
        }
        .dropdown-item:last-child {
          margin-bottom: 0;
        }
        .dropdown-item.highlighted {
          background: rgba(99, 102, 241, 0.15);
        }
        .dropdown-item.selected {
          background: var(--color-primary);
        }
        .dropdown-item.selected .item-ac,
        .dropdown-item.selected .item-district {
          color: rgba(255, 255, 255, 0.8);
        }
        .item-name {
          font-weight: 500;
          color: var(--text-primary);
        }
        .item-ac {
          font-size: 0.8rem;
          color: var(--text-muted);
          margin-left: 0.5rem;
          font-family: var(--font-heading);
        }
        .item-district {
          font-size: 0.8rem;
          color: var(--text-secondary);
          font-family: var(--font-heading);
        }
        .no-results {
          padding: 1.5rem;
          text-align: center;
          color: var(--text-muted);
        }
      `}</style>
    </div>
  );
};

import React, { useState, useEffect, useRef } from 'react';

interface ConstituencyItem {
  id: number;
  name: string;
  district: string;
  cluster_id: number | null;
}

interface ConstituencyMultiSelectProps {
  constituencies: ConstituencyItem[];
  selectedIds: number[];
  onAdd: (id: number) => void;
  onRemove: (id: number) => void;
}

export const ConstituencyMultiSelect: React.FC<ConstituencyMultiSelectProps> = ({
  constituencies,
  selectedIds,
  onAdd,
  onRemove,
}) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter out constituencies that are already selected
  const available = constituencies.filter((c) => !selectedIds.includes(c.id));

  // Filter based on search query
  const filtered = query
    ? available.filter(
        (c) =>
          c.name.toLowerCase().includes(query.toLowerCase()) ||
          c.district.toLowerCase().includes(query.toLowerCase()) ||
          c.id.toString() === query.trim()
      )
    : available;

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
    if (selectedIds.length >= 5) return;
    
    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'Enter') {
        setIsOpen(true);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1) % Math.max(1, filtered.length));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev - 1 + filtered.length) % Math.max(1, filtered.length));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (highlightedIndex >= 0 && highlightedIndex < filtered.length) {
        selectItem(filtered[highlightedIndex]);
      } else if (filtered.length > 0) {
        selectItem(filtered[0]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const selectItem = (item: ConstituencyItem) => {
    if (selectedIds.length >= 5) return;
    onAdd(item.id);
    setQuery('');
    setIsOpen(false);
    setHighlightedIndex(-1);
    if (inputRef.current) inputRef.current.focus();
  };

  // Get selected items object array
  const selectedItems = selectedIds
    .map((id) => constituencies.find((c) => c.id === id))
    .filter((c): c is ConstituencyItem => !!c);

  const reachedMax = selectedIds.length >= 5;

  return (
    <div className="multi-select-workspace" ref={dropdownRef}>
      {/* Selected Chips Row */}
      {selectedItems.length > 0 && (
        <div className="selected-chips-row animate-fade-in">
          {selectedItems.map((item) => (
            <div key={item.id} className="constituency-chip">
              <div className="chip-label-section">
                <span className="chip-name">{item.name}</span>
                <span className="chip-meta">AC #{item.id} • {item.district}</span>
              </div>
              <button
                type="button"
                className="chip-remove-btn"
                onClick={() => onRemove(item.id)}
                title={`Remove ${item.name} from comparison`}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input Field Wrapper */}
      <div className={`search-input-wrapper ${reachedMax ? 'disabled' : ''}`}>
        <span className="search-icon">🔍</span>
        <input
          ref={inputRef}
          type="text"
          placeholder={
            reachedMax
              ? "Max 5 constituencies selected. Remove some to add more."
              : "Search constituency to add to comparison..."
          }
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
            setHighlightedIndex(0);
          }}
          onFocus={() => {
            if (!reachedMax) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          disabled={reachedMax}
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

      {/* Warnings & Help Text */}
      <div className="comparison-help-row">
        {selectedIds.length < 2 ? (
          <span className="comparison-warning text-warning">
            ⚠️ Select at least <strong>2</strong> constituencies (currently {selectedIds.length}) to compare.
          </span>
        ) : (
          <span className="comparison-success text-success">
            ✓ Comparing <strong>{selectedIds.length}</strong> of 5 constituencies.
          </span>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && !reachedMax && (
        <div className="search-dropdown glass-panel animate-fade-in">
          {filtered.length === 0 ? (
            <div className="no-results">No available constituencies found</div>
          ) : (
            <div className="dropdown-scroll-wrapper">
              {filtered.map((item, idx) => {
                const isHighlighted = idx === highlightedIndex;
                return (
                  <div
                    key={item.id}
                    onClick={() => selectItem(item)}
                    onMouseEnter={() => setHighlightedIndex(idx)}
                    className={`dropdown-item ${isHighlighted ? 'highlighted' : ''}`}
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
        .multi-select-workspace {
          position: relative;
          width: 100%;
          max-width: 800px;
          margin: 0 auto 2rem;
          z-index: 100;
        }
        .selected-chips-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
          justify-content: center;
        }
        .constituency-chip {
          background: rgba(99, 102, 241, 0.15);
          border: 1px solid rgba(99, 102, 241, 0.35);
          border-radius: var(--radius-md);
          padding: 0.5rem 0.75rem;
          display: inline-flex;
          align-items: center;
          gap: 0.75rem;
          box-shadow: var(--shadow-sm);
          transition: transform var(--transition-fast), border-color var(--transition-fast);
        }
        .constituency-chip:hover {
          transform: translateY(-1px);
          border-color: var(--color-primary);
        }
        .chip-label-section {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
        }
        .chip-name {
          font-weight: 600;
          font-size: 0.85rem;
          color: #fff;
        }
        .chip-meta {
          font-size: 0.7rem;
          color: var(--text-secondary);
        }
        .chip-remove-btn {
          background: rgba(255, 255, 255, 0.05);
          border: none;
          border-radius: 50%;
          color: var(--text-secondary);
          cursor: pointer;
          width: 18px;
          height: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.65rem;
          transition: background var(--transition-fast), color var(--transition-fast);
        }
        .chip-remove-btn:hover {
          background: var(--danger-bg);
          color: var(--danger);
        }
        .search-input-wrapper.disabled {
          background: rgba(22, 26, 43, 0.4);
          border-color: rgba(255, 255, 255, 0.05);
        }
        .search-input-wrapper.disabled input::placeholder {
          color: var(--text-muted);
        }
        .comparison-help-row {
          margin-top: 0.5rem;
          font-size: 0.8rem;
          text-align: center;
        }
        .text-warning {
          color: var(--warning);
        }
        .text-success {
          color: var(--success);
        }
      `}</style>
    </div>
  );
};

import { useState, type FormEvent } from "react";
import "./SearchBar.css";

interface Speaker {
  name: string;
  count: number;
}

interface SearchBarProps {
  onSearch: (query: string) => void;
  onClear: () => void;
  onHome: () => void;
  loading: boolean;
  hasResults: boolean;
  speakers: Speaker[];
  selectedCharacter: string | null;
  onCharacterChange: (character: string | null) => void;
}

export default function SearchBar({
  onSearch,
  onClear,
  onHome,
  loading,
  hasResults,
  speakers,
  selectedCharacter,
  onCharacterChange,
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  function handleClear() {
    setQuery("");
    onClear();
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSearch(query.trim());
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <span className="search-bar__title" onClick={onHome}>ひぐらし</span>

      <select
        className="search-bar__character-select"
        value={selectedCharacter ?? ""}
        onChange={(e) => onCharacterChange(e.target.value || null)}
      >
        <option value="">All Characters</option>
        {speakers.map((s) => (
          <option key={s.name} value={s.name}>
            {s.name}
          </option>
        ))}
      </select>

      <div className="search-bar__input-wrapper">
        <input
          className="search-bar__input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search Japanese or English text…"
        />
        {(query || hasResults) && (
          <button
            type="button"
            className="search-bar__clear"
            onClick={handleClear}
          >
            ×
          </button>
        )}
      </div>

      <button
        className="search-bar__submit"
        type="submit"
        disabled={loading}
      >
        {loading ? "…" : "Search"}
      </button>
    </form>
  );
}

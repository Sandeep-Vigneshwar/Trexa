import React, { useState } from 'react';
import './SearchBar.css';

interface SearchBarProps {
  onSearch: (query: string, directory: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [directory, setDirectory] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query, directory);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={directory}
        onChange={(e) => setDirectory(e.target.value)}
        placeholder="Directory to index..."
        style={{ marginRight: '8px' }}
      />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="File name or search query..."
        style={{ marginRight: '8px' }}
      />
      <button type="submit">Search</button>
    </form>
  );
};

export default SearchBar;

import { useState } from 'react';
import './App.css';
import ResultCard from './components/ResultCard';
import Graph3D from './components/Graph3D';

interface SearchResult {
  file_path: string;
  file_name: string;
  score: number;
}

function App() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [directory, setDirectory] = useState('');
  const [query, setQuery] = useState('');
  const [isMapped, setIsMapped] = useState(false);
  const [isMapping, setIsMapping] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [showGraph, setShowGraph] = useState(false);

  const handleMap = async () => {
    setErrorMsg(null);
    setIsMapping(true);
    setIsMapped(false);
    setResults([]);
    try {
      const api = await import('./services/api');
      const res = await api.startIndexing(directory);
      if (res.status === 'success') {
        setIsMapped(true);
      } else {
        setErrorMsg('Mapping failed.');
      }
    } catch (error: any) {
      setErrorMsg(error?.message || 'Mapping failed.');
    }
    setIsMapping(false);
  };

  const handleSearch = async () => {
    setErrorMsg(null);
    setIsSearching(true);
    setResults([]);
    try {
      const api = await import('./services/api');
      const data = await api.searchFiles(query, 5);
      if (!data || !Array.isArray(data.results)) {
        setResults([]);
        setErrorMsg(data?.detail || 'No results found or backend error.');
      } else {
        const mappedResults = data.results.map((result: any) => ({
          file_path: result.file_path || 'Unknown',
          file_name: result.file_name || 'Unknown',
          score: typeof result.score === 'number' ? result.score : undefined,
        }));
        setResults(mappedResults);
      }
    } catch (error: any) {
      setResults([]);
      setErrorMsg(error?.message || 'Search failed.');
      console.error('Search failed:', error);
    }
    setIsSearching(false);
  };

  return (
    <div className="App">
      <h1>Trexa</h1>
      <div className="workflow-controls">
        <input
          type="text"
          value={directory}
          onChange={e => setDirectory(e.target.value)}
          placeholder="Directory to index..."
          style={{ marginRight: '8px' }}
          disabled={isMapping || isSearching}
        />
        <button onClick={handleMap} disabled={!directory || isMapping || isSearching}>
          {isMapping ? 'Mapping...' : 'Map'}
        </button>
        <button
          onClick={() => setShowGraph(true)}
          disabled={!isMapped || isMapping || isSearching}
          style={{ fontSize: 16, padding: '8px 18px' }}
        >
          View Map
        </button>
      </div>
      {showGraph && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: '#fff', zIndex: 1000 }}>
          <button
            style={{ position: 'absolute', top: 24, right: 24, zIndex: 1010, fontSize: 18, padding: '10px 24px' }}
            onClick={() => setShowGraph(false)}
          >
            Exit
          </button>
          <div style={{ width: '100vw', height: '100vh' }}>
            <Graph3D directory={directory} />
          </div>
        </div>
      )}
      <div className="workflow-controls">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="File name or search query..."
          style={{ marginRight: '8px' }}
          disabled={!isMapped || isMapping || isSearching}
        />
        <button onClick={handleSearch} disabled={!isMapped || !query || isSearching || isMapping}>
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>
      {isMapped && <div style={{ color: 'green', marginBottom: '1em' }}>Mapping complete. You can now search.</div>}
      {errorMsg && <div style={{ color: 'red', margin: '1em 0' }}>{errorMsg}</div>}
      {results.length > 0 && results.map((result, idx) => (
        <ResultCard
          key={idx}
          filePath={result.file_path}
          fileName={result.file_name}
          score={result.score}
        />
      ))}
    </div>
  );
}

export default App;

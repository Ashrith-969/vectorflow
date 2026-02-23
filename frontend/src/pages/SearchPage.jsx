import { useState } from 'react';
import { useLazyQuery } from '@apollo/client';
import { SEARCH } from '../graphql/queries';
import SearchResultCard from '../components/SearchResultCard';
import SearchDetailModal from '../components/SearchDetailModal';
import { Search, Loader2 } from 'lucide-react';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [selectedResult, setSelectedResult] = useState(null);

  const [searchQuery, { data, loading, error }] = useLazyQuery(SEARCH);

  const handleSearch = (e) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    searchQuery({ variables: { query: q, limit: 5 } });
  };

  const results = data?.search?.results || [];

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-800">Search Documents</h1>
        <p className="text-sm text-gray-500">Find relevant documents using semantic search</p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-2xl mx-auto">
          <form onSubmit={handleSearch} className="mb-8">
            <div className="relative">
              <Search size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search your documents..."
                className="w-full bg-white border border-gray-300 rounded-xl pl-12 pr-28 py-4 text-base focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none shadow-sm"
              />
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="absolute right-2 top-1/2 -translate-y-1/2 btn-primary flex items-center gap-2 text-sm"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                Search
              </button>
            </div>
          </form>

          {error && (
            <div className="bg-red-50 text-red-600 text-sm px-4 py-3 rounded-lg border border-red-100 mb-4">
              {error.message}
            </div>
          )}

          {data && (
            <div className="mb-4">
              <p className="text-sm text-gray-500">
                {results.length} result{results.length !== 1 && 's'} for "<span className="font-medium text-gray-700">{data.search.query}</span>"
              </p>
            </div>
          )}

          <div className="space-y-3">
            {results.map((result) => (
              <SearchResultCard
                key={result.id}
                result={result}
                onClick={setSelectedResult}
              />
            ))}
          </div>

          {data && results.length === 0 && (
            <div className="text-center py-12">
              <Search size={48} className="mx-auto text-gray-300 mb-3" />
              <p className="text-gray-500">No results found. Try a different query.</p>
            </div>
          )}
        </div>
      </div>

      <SearchDetailModal
        result={selectedResult}
        onClose={() => setSelectedResult(null)}
      />
    </div>
  );
}

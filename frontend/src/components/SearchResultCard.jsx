import { FileText } from 'lucide-react';

export default function SearchResultCard({ result, onClick }) {
  const pct = Math.round(result.score * 100);
  const color = pct >= 80 ? 'text-green-600 bg-green-50' : pct >= 60 ? 'text-yellow-600 bg-yellow-50' : 'text-red-600 bg-red-50';

  return (
    <button
      onClick={() => onClick(result)}
      className="w-full text-left card hover:shadow-md hover:border-indigo-200 transition-all group cursor-pointer"
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-indigo-100 transition-colors">
          <FileText size={20} className="text-indigo-600" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-800 group-hover:text-indigo-600 transition-colors truncate">
            {result.title}
          </h3>
          {result.metadata?.category && (
            <span className="text-xs text-gray-400">{result.metadata.category}</span>
          )}
        </div>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${color}`}>
          {pct}%
        </span>
      </div>
    </button>
  );
}

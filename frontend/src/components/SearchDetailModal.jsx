import { X, FileText, Tag } from 'lucide-react';

export default function SearchDetailModal({ result, onClose }) {
  if (!result) return null;

  const pct = Math.round(result.score * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-50 rounded-lg flex items-center justify-center">
              <FileText size={20} className="text-indigo-600" />
            </div>
            <div>
              <h2 className="font-bold text-lg text-gray-800">{result.title}</h2>
              <p className="text-xs text-gray-400">ID: {result.documentId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg hover:bg-gray-100 flex items-center justify-center transition-colors"
          >
            <X size={18} className="text-gray-500" />
          </button>
        </div>

        <div className="p-6 overflow-auto flex-1">
          <div className="flex items-center gap-3 mb-5">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Similarity</span>
              <div className="w-24 h-2 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-indigo-500 rounded-full"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="text-sm font-bold text-indigo-600">{pct}%</span>
            </div>
          </div>

          <div className="mb-5">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Content</h3>
            <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
              {result.snippet}
            </div>
          </div>

          {(result.metadata?.category || result.metadata?.tags?.length > 0) && (
            <div>
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Metadata</h3>
              <div className="flex flex-wrap gap-2">
                {result.metadata.category && (
                  <span className="inline-flex items-center gap-1 text-xs bg-purple-50 text-purple-700 px-2.5 py-1 rounded-full font-medium">
                    <FileText size={12} />
                    {result.metadata.category}
                  </span>
                )}
                {result.metadata.tags?.map((tag, i) => (
                  <span key={i} className="inline-flex items-center gap-1 text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full font-medium">
                    <Tag size={12} />
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

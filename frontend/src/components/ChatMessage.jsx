import { useState } from 'react';
import { Bot, User, ChevronDown, ChevronUp } from 'lucide-react';

function ConfidenceBar({ confidence }) {
  const pct = Math.round(confidence * 100);
  const color = pct >= 75 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="flex items-center gap-2 mt-2">
      <span className="text-xs text-gray-500">Confidence</span>
      <div className="flex-1 h-1.5 bg-gray-200 rounded-full max-w-[120px]">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-medium text-gray-600">{pct}%</span>
    </div>
  );
}

export default function ChatMessage({ message }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="flex items-end gap-2 max-w-[70%]">
          <div className="bg-indigo-600 text-white px-4 py-3 rounded-2xl rounded-br-sm text-sm leading-relaxed">
            {message.content}
          </div>
          <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
            <User size={16} className="text-indigo-600" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-end gap-2 max-w-[75%]">
        <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot size={16} className="text-white" />
        </div>
        <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm border border-gray-100 text-sm leading-relaxed">
          <p className="whitespace-pre-wrap">{message.content}</p>

          {message.confidence != null && (
            <ConfidenceBar confidence={message.confidence} />
          )}

          {message.sources?.length > 0 && (
            <div className="mt-3 pt-2 border-t border-gray-100">
              <button
                onClick={() => setSourcesOpen(!sourcesOpen)}
                className="flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800"
              >
                {sourcesOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                {sourcesOpen ? 'Hide' : 'View'} {message.sources.length} source{message.sources.length !== 1 && 's'}
              </button>

              {sourcesOpen && (
                <div className="mt-2 space-y-2">
                  {message.sources.map((src, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3 text-xs">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-gray-700">{src.title}</span>
                        <span className="text-gray-400">{Math.round(src.relevance * 100)}% relevant</span>
                      </div>
                      <p className="text-gray-600 line-clamp-3">{src.snippet}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

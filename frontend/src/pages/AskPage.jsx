import { useState, useRef, useEffect } from 'react';
import { useLazyQuery } from '@apollo/client';
import { ASK } from '../graphql/queries';
import ChatMessage from '../components/ChatMessage';
import { Send, Loader2, Sparkles } from 'lucide-react';

export default function AskPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  const [askQuery, { loading }] = useLazyQuery(ASK, {
    onCompleted: (data) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.ask.answer,
        confidence: data.ask.confidence,
        sources: data.ask.sources,
      }]);
    },
    onError: (err) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${err.message}`,
      }]);
    },
  });

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = () => {
    const q = input.trim();
    if (!q || loading) return;

    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setInput('');
    askQuery({ variables: { question: q, maxSources: 5 } });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-800">Ask AI</h1>
        <p className="text-sm text-gray-500">Ask questions and get AI-generated answers from your documents</p>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-auto p-6 chat-scroll">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center mb-4">
              <Sparkles size={32} className="text-indigo-500" />
            </div>
            <h2 className="text-lg font-semibold text-gray-700 mb-1">What would you like to know?</h2>
            <p className="text-sm text-gray-400 max-w-md">
              Ask a question about your ingested documents. The AI will search through them and provide an answer with sources.
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}

        {loading && (
          <div className="flex justify-start mb-4">
            <div className="flex items-center gap-2 bg-white px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm border border-gray-100">
              <Loader2 size={16} className="animate-spin text-indigo-500" />
              <span className="text-sm text-gray-500">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question..."
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="btn-primary px-4 flex items-center gap-2"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

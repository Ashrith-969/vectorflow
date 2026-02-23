import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { BULK_INGEST } from '../graphql/mutations';
import { Files, Plus, Trash2, Loader2, CheckCircle, XCircle, FileJson } from 'lucide-react';

const emptyDoc = () => ({ title: '', content: '', category: '', tags: '' });

/** Parse pasted JSON into documents array. Accepts { documents: [...] } or [...]. */
function parseJsonToDocuments(raw) {
  const trimmed = raw.trim();
  if (!trimmed) return { documents: [], error: 'Paste JSON first.' };
  let parsed;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    return { documents: [], error: 'Invalid JSON.' };
  }
  let list = Array.isArray(parsed) ? parsed : parsed?.documents;
  if (!Array.isArray(list)) {
    return { documents: [], error: 'Use { "documents": [...] } or an array of documents.' };
  }
  const documents = list
    .map((d) => {
      if (!d || typeof d.title !== 'string' || typeof d.content !== 'string') return null;
      const title = d.title.trim();
      const content = d.content.trim();
      if (!title || !content) return null;
      let metadata = null;
      if (d.metadata && typeof d.metadata === 'object') {
        const cat = d.metadata.category != null ? String(d.metadata.category) : null;
        const tags = Array.isArray(d.metadata.tags)
          ? d.metadata.tags.map((t) => String(t)).filter(Boolean)
          : typeof d.metadata.tags === 'string'
            ? d.metadata.tags.split(',').map((t) => t.trim()).filter(Boolean)
            : null;
        if (cat || (tags && tags.length)) metadata = { category: cat || null, tags: tags || null };
      }
      return { title, content, metadata };
    })
    .filter(Boolean);
  return { documents, error: documents.length === 0 ? 'No valid documents (need title and content).' : null };
}

export default function BulkIngestPage() {
  const [mode, setMode] = useState('form'); // 'form' | 'json'
  const [docs, setDocs] = useState([emptyDoc(), emptyDoc()]);
  const [jsonInput, setJsonInput] = useState('');
  const [jsonError, setJsonError] = useState(null);
  const [result, setResult] = useState(null);

  const [bulkIngestMutation, { loading }] = useMutation(BULK_INGEST);

  const updateDoc = (index, field, value) => {
    setDocs(prev => prev.map((d, i) => i === index ? { ...d, [field]: value } : d));
  };

  const addDoc = () => setDocs(prev => [...prev, emptyDoc()]);

  const removeDoc = (index) => {
    if (docs.length <= 1) return;
    setDocs(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);

    const documents = docs
      .filter(d => d.title.trim() && d.content.trim())
      .map(d => {
        const tags = d.tags ? d.tags.split(',').map(t => t.trim()).filter(Boolean) : null;
        const metadata = (d.category || tags?.length)
          ? { category: d.category || null, tags }
          : null;
        return { title: d.title, content: d.content, metadata };
      });

    if (documents.length === 0) return;

    try {
      const { data } = await bulkIngestMutation({
        variables: { input: { documents } },
      });
      setResult(data.bulkIngest);
      setDocs([emptyDoc(), emptyDoc()]);
    } catch (err) {
      setResult({ error: err.message });
    }
  };

  const handleJsonSubmit = async () => {
    setResult(null);
    setJsonError(null);
    const { documents, error } = parseJsonToDocuments(jsonInput);
    if (error) {
      setJsonError(error);
      return;
    }
    try {
      const { data } = await bulkIngestMutation({
        variables: { input: { documents } },
      });
      setResult(data.bulkIngest);
      setJsonInput('');
    } catch (err) {
      setResult({ error: err.message });
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-800">Bulk Ingest</h1>
        <p className="text-sm text-gray-500">Ingest multiple documents at once</p>
        <div className="flex gap-1 mt-3">
          <button
            type="button"
            onClick={() => { setMode('form'); setJsonError(null); setResult(null); }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium ${mode === 'form' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
          >
            Form
          </button>
          <button
            type="button"
            onClick={() => { setMode('json'); setResult(null); }}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5 ${mode === 'json' ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
          >
            <FileJson size={16} />
            Paste JSON
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto">
          {result && !result.error && (
            <div className="mb-6 card border-green-200 bg-green-50">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle size={20} className="text-green-600" />
                <span className="font-semibold text-green-800">Bulk ingestion complete</span>
              </div>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-3 bg-white rounded-lg">
                  <p className="text-2xl font-bold text-gray-800">{result.total}</p>
                  <p className="text-xs text-gray-500">Total</p>
                </div>
                <div className="text-center p-3 bg-white rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{result.successful}</p>
                  <p className="text-xs text-gray-500">Successful</p>
                </div>
                <div className="text-center p-3 bg-white rounded-lg">
                  <p className="text-2xl font-bold text-red-600">{result.failed}</p>
                  <p className="text-xs text-gray-500">Failed</p>
                </div>
              </div>
              <div className="space-y-2">
                {result.results.map((r, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    {r.status === 'COMPLETED' ? (
                      <CheckCircle size={14} className="text-green-500" />
                    ) : (
                      <XCircle size={14} className="text-red-500" />
                    )}
                    <span className="font-medium">{r.title}</span>
                    <span className="text-gray-400">— {r.chunkCount} chunks</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result?.error && (
            <div className="mb-6 p-4 rounded-xl border bg-red-50 border-red-200 flex items-center gap-2 text-sm text-red-800">
              <XCircle size={18} className="text-red-600" />
              {result.error}
            </div>
          )}

          {mode === 'json' && (
            <div className="space-y-3 mb-6">
              <label className="block text-sm font-medium text-gray-700">Paste JSON</label>
              <textarea
                value={jsonInput}
                onChange={(e) => { setJsonInput(e.target.value); setJsonError(null); }}
                placeholder={'{"documents":[{"title":"...","content":"...","metadata":{"category":"...","tags":[]}}]}'}
                className="input-field min-h-[220px] resize-y font-mono text-sm"
                spellCheck={false}
              />
              {jsonError && (
                <p className="text-sm text-red-600 flex items-center gap-1.5">
                  <XCircle size={14} />
                  {jsonError}
                </p>
              )}
              <button
                type="button"
                onClick={handleJsonSubmit}
                disabled={loading || !jsonInput.trim()}
                className="btn-primary flex items-center gap-2 text-sm"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : <FileJson size={16} />}
                {loading ? 'Ingesting...' : 'Ingest from JSON'}
              </button>
            </div>
          )}

          {mode === 'form' && (
          <form onSubmit={handleSubmit} className="space-y-4">
            {docs.map((doc, i) => (
              <div key={i} className="card relative">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-semibold text-gray-500">Document {i + 1}</span>
                  {docs.length > 1 && (
                    <button type="button" onClick={() => removeDoc(i)} className="text-gray-400 hover:text-red-500">
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
                <div className="space-y-3">
                  <input
                    type="text"
                    value={doc.title}
                    onChange={(e) => updateDoc(i, 'title', e.target.value)}
                    className="input-field"
                    placeholder="Title"
                    required
                  />
                  <textarea
                    value={doc.content}
                    onChange={(e) => updateDoc(i, 'content', e.target.value)}
                    className="input-field min-h-[100px] resize-y"
                    placeholder="Content"
                    required
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      type="text"
                      value={doc.category}
                      onChange={(e) => updateDoc(i, 'category', e.target.value)}
                      className="input-field"
                      placeholder="Category (optional)"
                    />
                    <input
                      type="text"
                      value={doc.tags}
                      onChange={(e) => updateDoc(i, 'tags', e.target.value)}
                      className="input-field"
                      placeholder="Tags (comma-separated)"
                    />
                  </div>
                </div>
              </div>
            ))}

            <div className="flex gap-3">
              <button type="button" onClick={addDoc} className="btn-secondary flex items-center gap-2 text-sm">
                <Plus size={16} />
                Add Document
              </button>
              <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2 text-sm">
                {loading ? <Loader2 size={16} className="animate-spin" /> : <Files size={16} />}
                {loading ? 'Ingesting...' : `Ingest ${docs.filter(d => d.title && d.content).length} Documents`}
              </button>
            </div>
          </form>
          )}
        </div>
      </div>
    </div>
  );
}

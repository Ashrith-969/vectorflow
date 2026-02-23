import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { INGEST } from '../graphql/mutations';
import { Upload, Loader2, CheckCircle, XCircle, X } from 'lucide-react';

export default function IngestPage() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [tags, setTags] = useState([]);
  const [result, setResult] = useState(null);

  const [ingestMutation, { loading }] = useMutation(INGEST);

  const handleAddTag = (e) => {
    if (e.key === 'Enter' && tagsInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagsInput.trim())) {
        setTags([...tags, tagsInput.trim()]);
      }
      setTagsInput('');
    }
  };

  const removeTag = (tag) => setTags(tags.filter(t => t !== tag));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult(null);
    try {
      const metadata = (category || tags.length > 0)
        ? { category: category || null, tags: tags.length > 0 ? tags : null }
        : null;

      const { data } = await ingestMutation({
        variables: { input: { title, content, metadata } },
      });

      setResult({ success: true, data: data.ingest });
      setTitle('');
      setContent('');
      setCategory('');
      setTags([]);
    } catch (err) {
      setResult({ success: false, message: err.message });
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-800">Ingest Document</h1>
        <p className="text-sm text-gray-500">Add a new document to the vector database</p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-2xl mx-auto">
          {result && (
            <div className={`mb-6 p-4 rounded-xl border flex items-start gap-3 ${
              result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
            }`}>
              {result.success ? (
                <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
              ) : (
                <XCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
              )}
              <div className="text-sm">
                {result.success ? (
                  <>
                    <p className="font-medium text-green-800">Document ingested successfully!</p>
                    <p className="text-green-600 mt-1">
                      "{result.data.title}" — {result.data.chunkCount} chunks created
                    </p>
                  </>
                ) : (
                  <p className="font-medium text-red-800">{result.message}</p>
                )}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="card space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="input-field"
                placeholder="Document title"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="input-field min-h-[200px] resize-y"
                placeholder="Paste your document content here..."
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category (optional)</label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="input-field"
                  placeholder="e.g. database, api"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tags (optional)</label>
                <input
                  type="text"
                  value={tagsInput}
                  onChange={(e) => setTagsInput(e.target.value)}
                  onKeyDown={handleAddTag}
                  className="input-field"
                  placeholder="Type & press Enter"
                />
              </div>
            </div>

            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {tags.map(tag => (
                  <span key={tag} className="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 text-xs px-2.5 py-1 rounded-full font-medium">
                    {tag}
                    <button type="button" onClick={() => removeTag(tag)} className="hover:text-indigo-900">
                      <X size={12} />
                    </button>
                  </span>
                ))}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
              {loading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
              {loading ? 'Ingesting...' : 'Ingest Document'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

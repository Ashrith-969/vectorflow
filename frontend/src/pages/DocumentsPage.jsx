import { useState } from 'react';
import { useQuery } from '@apollo/client';
import { DOCUMENTS } from '../graphql/queries';
import DocumentDetailModal from '../components/DocumentDetailModal';
import { FileText, Loader2, ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE = 20;

export default function DocumentsPage() {
  const [page, setPage] = useState(1);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const { data, loading, error } = useQuery(DOCUMENTS, {
    variables: { page, pageSize: PAGE_SIZE },
  });

  const list = data?.documents;
  const documents = list?.documents ?? [];
  const totalCount = list?.totalCount ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <div className="h-full flex flex-col">
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <h1 className="text-xl font-bold text-gray-800">Documents</h1>
        <p className="text-sm text-gray-500">All ingested documents (Admin & Editor)</p>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          {error && (
            <div className="mb-6 p-4 rounded-xl border bg-red-50 border-red-200 flex items-center gap-2 text-sm text-red-800">
              {error.message}
            </div>
          )}

          {loading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 size={24} className="animate-spin text-indigo-500" />
            </div>
          )}

          {!loading && !error && (
            <>
              <p className="text-sm text-gray-500 mb-4">
                {totalCount} document{totalCount !== 1 ? 's' : ''} total
              </p>

              <div className="space-y-3">
                {documents.length === 0 ? (
                  <div className="card text-center py-12">
                    <FileText size={48} className="mx-auto text-gray-300 mb-3" />
                    <p className="text-gray-500">No documents yet. Ingest or bulk-ingest to get started.</p>
                  </div>
                ) : (
                  documents.map((doc) => (
                    <button
                      key={doc.documentId}
                      type="button"
                      onClick={() => setSelectedDocument(doc)}
                      className="w-full text-left card flex items-start gap-4 hover:shadow-md hover:border-indigo-200 transition-all group cursor-pointer"
                    >
                      <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0 group-hover:bg-indigo-100 transition-colors">
                        <FileText size={20} className="text-indigo-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-800 truncate group-hover:text-indigo-600 transition-colors">{doc.title}</h3>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {doc.chunkCount} chunk{doc.chunkCount !== 1 ? 's' : ''}
                          {doc.createdAt && ` · ${doc.createdAt}`}
                        </p>
                        {doc.metadata && (doc.metadata.category || doc.metadata.tags?.length) && (
                          <p className="text-xs text-gray-400 mt-1">
                            {doc.metadata.category && <span>{doc.metadata.category}</span>}
                            {doc.metadata.tags?.length > 0 && (
                              <span className="ml-1">
                                {doc.metadata.tags.join(', ')}
                              </span>
                            )}
                          </p>
                        )}
                      </div>
                      <code className="text-xs text-gray-400 truncate max-w-[140px]" title={doc.documentId}>
                        {doc.documentId}
                      </code>
                    </button>
                  ))
                )}
              </div>

              {totalPages > 1 && (
                <div className="mt-6 flex items-center justify-between">
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="btn-secondary flex items-center gap-1.5 text-sm disabled:opacity-50"
                  >
                    <ChevronLeft size={16} />
                    Previous
                  </button>
                  <span className="text-sm text-gray-600">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                    className="btn-secondary flex items-center gap-1.5 text-sm disabled:opacity-50"
                  >
                    Next
                    <ChevronRight size={16} />
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <DocumentDetailModal
        documentId={selectedDocument?.documentId ?? null}
        onClose={() => setSelectedDocument(null)}
      />
    </div>
  );
}

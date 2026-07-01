import { useEffect } from 'react'
import { Database, RefreshCw } from 'lucide-react'
import { useDocumentStore } from '../../store/documentStore'
import { DropZone } from './DropZone'
import { DocumentItem } from './DocumentItem'

export function DocumentPanel() {
  const { documents, isLoading, fetchDocuments } = useDocumentStore()

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  return (
    <aside className="w-72 shrink-0 flex flex-col h-full bg-surface-800 border-r border-surface-600">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-surface-600">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-brand-400" />
          <h2 className="text-sm font-semibold text-gray-200">Documents</h2>
          {documents.length > 0 && (
            <span className="badge bg-brand-500/20 text-brand-300">{documents.length}</span>
          )}
        </div>
        <button
          onClick={fetchDocuments}
          disabled={isLoading}
          className="btn-ghost p-1.5"
          title="Refresh documents"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Upload zone */}
      <div className="px-4 py-4 border-b border-surface-600">
        <DropZone />
      </div>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {isLoading && documents.length === 0 ? (
          <div className="flex items-center justify-center py-12 text-gray-500 text-sm">
            <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            Loading…
          </div>
        ) : documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center gap-2">
            <Database className="w-8 h-8 text-surface-500" />
            <p className="text-sm text-gray-500">No documents yet</p>
            <p className="text-xs text-gray-600">Upload a file to get started</p>
          </div>
        ) : (
          <div className="space-y-1">
            {documents.map((doc) => (
              <DocumentItem key={doc.file_id} document={doc} />
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}

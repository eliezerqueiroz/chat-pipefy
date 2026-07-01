import { useState } from 'react'
import { FileText, Trash2, ChevronDown, ChevronUp } from 'lucide-react'
import type { Document } from '../../types'
import { useDocumentStore } from '../../store/documentStore'

interface Props {
  document: Document
}

export function DocumentItem({ document: doc }: Props) {
  const [confirmDelete, setConfirmDelete] = useState(false)
  const { removeDocument } = useDocumentStore()

  const formattedDate = new Date(doc.uploaded_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className="group flex items-start gap-3 p-3 rounded-lg hover:bg-surface-700 transition-colors duration-150 animate-fade-in">
      {/* File icon */}
      <div className="p-1.5 rounded-md bg-brand-500/15 shrink-0 mt-0.5">
        <FileText className="w-3.5 h-3.5 text-brand-400" />
      </div>

      {/* Metadata */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-200 truncate" title={doc.name}>
          {doc.name}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">
          {doc.chunks} chunks · {formattedDate}
        </p>
      </div>

      {/* Delete button */}
      <div className="shrink-0">
        {confirmDelete ? (
          <div className="flex gap-1">
            <button
              onClick={() => removeDocument(doc.file_id)}
              className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
            >
              Confirm
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="text-xs px-2 py-1 rounded bg-surface-600 text-gray-400 hover:bg-surface-500 transition-colors"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmDelete(true)}
            className="opacity-0 group-hover:opacity-100 p-1.5 rounded-md text-gray-500 hover:text-red-400 hover:bg-red-400/10 transition-all duration-150"
            title="Delete document"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  )
}

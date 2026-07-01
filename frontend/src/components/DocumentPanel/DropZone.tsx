import { useState, useCallback } from 'react'
import { Upload, FileText, AlertCircle, CheckCircle2, X } from 'lucide-react'
import { useDocumentStore } from '../../store/documentStore'

const ACCEPTED = '.pdf,.txt,.docx'
const MAX_MB = 20

export function DropZone() {
  const [isDragOver, setIsDragOver] = useState(false)
  const [lastStatus, setLastStatus] = useState<'success' | 'error' | null>(null)
  const { isUploading, uploadProgress, uploadFile, error, clearError } = useDocumentStore()

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return
      const file = files[0]

      if (file.size > MAX_MB * 1024 * 1024) {
        alert(`File is too large. Maximum allowed size is ${MAX_MB} MB.`)
        return
      }

      clearError()
      await uploadFile(file)
      setLastStatus(error ? 'error' : 'success')
      setTimeout(() => setLastStatus(null), 3000)
    },
    [uploadFile, clearError, error]
  )

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    handleFiles(e.dataTransfer.files)
  }

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <label
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={onDrop}
        className={`
          relative flex flex-col items-center gap-3 p-6 rounded-xl border-2 border-dashed
          cursor-pointer transition-all duration-200
          ${isDragOver
            ? 'border-brand-500 bg-brand-500/10'
            : 'border-surface-500 hover:border-brand-500/60 hover:bg-surface-700/50'
          }
          ${isUploading ? 'pointer-events-none opacity-75' : ''}
        `}
      >
        <input
          type="file"
          accept={ACCEPTED}
          className="sr-only"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={isUploading}
        />

        <div className={`p-3 rounded-full transition-colors ${isDragOver ? 'bg-brand-500/20' : 'bg-surface-600'}`}>
          <Upload className={`w-5 h-5 ${isDragOver ? 'text-brand-400' : 'text-gray-400'}`} />
        </div>

        <div className="text-center">
          <p className="text-sm font-medium text-gray-300">
            {isDragOver ? 'Drop to upload' : 'Drop file or click to browse'}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">PDF, TXT, DOCX · Max {MAX_MB} MB</p>
        </div>
      </label>

      {/* Upload progress */}
      {isUploading && (
        <div className="space-y-1.5 animate-fade-in">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Uploading & indexing…</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="h-1.5 bg-surface-600 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-500 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Status feedback */}
      {lastStatus === 'success' && !isUploading && (
        <div className="flex items-center gap-2 text-xs text-emerald-400 animate-fade-in">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Document indexed successfully!</span>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg animate-fade-in">
          <AlertCircle className="w-3.5 h-3.5 text-red-400 mt-0.5 shrink-0" />
          <p className="text-xs text-red-300 flex-1">{error}</p>
          <button onClick={clearError} className="text-red-400 hover:text-red-300">
            <X className="w-3 h-3" />
          </button>
        </div>
      )}
    </div>
  )
}

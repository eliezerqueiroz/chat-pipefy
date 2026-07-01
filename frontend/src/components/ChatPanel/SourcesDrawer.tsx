import { useState } from 'react'
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react'
import type { Source } from '../../types'

interface Props {
  sources: Source[]
}

export function SourcesDrawer({ sources }: Props) {
  const [isOpen, setIsOpen] = useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-2">
      <button
        onClick={() => setIsOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-brand-400 transition-colors"
      >
        <FileText className="w-3 h-3" />
        <span>{sources.length} source{sources.length > 1 ? 's' : ''}</span>
        {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      {isOpen && (
        <div className="mt-2 space-y-2 animate-fade-in">
          {sources.map((src, idx) => (
            <div key={idx} className="p-3 rounded-lg bg-surface-700/60 border border-surface-500/50">
              <div className="flex items-center gap-1.5 mb-1.5">
                <FileText className="w-3 h-3 text-brand-400 shrink-0" />
                <span className="text-xs font-medium text-brand-300 truncate">{src.source}</span>
                <span className="text-xs text-gray-600 ml-auto shrink-0">chunk #{src.chunk_index}</span>
              </div>
              <p className="text-xs text-gray-400 leading-relaxed line-clamp-4">{src.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

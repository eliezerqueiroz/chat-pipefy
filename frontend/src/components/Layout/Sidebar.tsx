import { useState } from 'react'
import { Plus, MessageSquare, Pencil, Trash2, Check, X } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'

export function Sidebar() {
  const {
    sessions,
    activeSessionId,
    createNewSession,
    setActiveSession,
    renameSession,
    deleteSession,
  } = useChatStore()

  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')

  const startEdit = (id: string, name: string) => {
    setEditingId(id)
    setEditName(name)
  }

  const confirmRename = (id: string) => {
    if (editName.trim()) renameSession(id, editName.trim())
    setEditingId(null)
  }

  return (
    <div className="w-56 shrink-0 flex flex-col h-full bg-surface-900 border-r border-surface-600">
      {/* Logo + brand */}
      <div className="px-4 py-5 border-b border-surface-700">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-100 leading-none">Chat-Pipefy</p>
            <p className="text-xs text-gray-500 leading-none mt-0.5">AI Document Chat</p>
          </div>
        </div>
      </div>

      {/* New session button */}
      <div className="px-3 py-3">
        <button
          id="new-session-btn"
          onClick={() => createNewSession()}
          className="btn-primary w-full justify-center text-xs py-2"
        >
          <Plus className="w-3.5 h-3.5" />
          New Chat
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5">
        {sessions.length === 0 && (
          <p className="text-xs text-gray-600 text-center py-6 px-2">
            No sessions yet.<br />Click "New Chat" to start.
          </p>
        )}

        {sessions.map((sess) => (
          <div
            key={sess.id}
            onClick={() => setActiveSession(sess.id)}
            className={`group relative flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer
              transition-colors duration-150
              ${activeSessionId === sess.id
                ? 'bg-brand-500/20 border border-brand-500/30'
                : 'hover:bg-surface-700'
              }`}
          >
            <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${activeSessionId === sess.id ? 'text-brand-400' : 'text-gray-500'}`} />

            {editingId === sess.id ? (
              <input
                autoFocus
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') confirmRename(sess.id)
                  if (e.key === 'Escape') setEditingId(null)
                }}
                onClick={(e) => e.stopPropagation()}
                className="flex-1 bg-transparent text-xs text-gray-100 outline-none border-b border-brand-500"
              />
            ) : (
              <span className={`flex-1 text-xs truncate ${activeSessionId === sess.id ? 'text-gray-200 font-medium' : 'text-gray-400'}`}>
                {sess.name}
              </span>
            )}

            {/* Action buttons */}
            {editingId === sess.id ? (
              <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                <button onClick={() => confirmRename(sess.id)} className="text-emerald-400 hover:text-emerald-300">
                  <Check className="w-3 h-3" />
                </button>
                <button onClick={() => setEditingId(null)} className="text-gray-500 hover:text-gray-300">
                  <X className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <div className="hidden group-hover:flex gap-1" onClick={(e) => e.stopPropagation()}>
                <button
                  onClick={() => startEdit(sess.id, sess.name)}
                  className="text-gray-500 hover:text-gray-300 p-0.5 rounded"
                >
                  <Pencil className="w-3 h-3" />
                </button>
                <button
                  onClick={() => deleteSession(sess.id)}
                  className="text-gray-500 hover:text-red-400 p-0.5 rounded"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

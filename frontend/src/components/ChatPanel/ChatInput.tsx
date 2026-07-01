import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'

export function ChatInput() {
  const [text, setText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { sendMessage, isStreaming, activeSession } = useChatStore()
  const session = activeSession()

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [text])

  const handleSubmit = async () => {
    const trimmed = text.trim()
    if (!trimmed || isStreaming || !session) return
    setText('')
    await sendMessage(trimmed)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="flex items-end gap-3 p-4 border-t border-surface-600 bg-surface-800">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={session ? 'Ask a question about your documents…' : 'Create or select a chat session first'}
          disabled={isStreaming || !session}
          rows={1}
          className={`
            w-full resize-none bg-surface-700 border border-surface-500 rounded-xl px-4 py-3 pr-12
            text-sm text-gray-100 placeholder-gray-500 outline-none
            focus:border-brand-500 focus:ring-1 focus:ring-brand-500
            transition-colors duration-150 max-h-40
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
        />
      </div>

      <button
        id="chat-send-btn"
        onClick={handleSubmit}
        disabled={!text.trim() || isStreaming || !session}
        className="shrink-0 w-10 h-10 flex items-center justify-center rounded-xl bg-brand-500
                   hover:bg-brand-600 active:bg-brand-700 disabled:opacity-40
                   disabled:cursor-not-allowed transition-all duration-150"
        title="Send message (Enter)"
      >
        {isStreaming ? (
          <Loader2 className="w-4 h-4 text-white animate-spin" />
        ) : (
          <Send className="w-4 h-4 text-white" />
        )}
      </button>
    </div>
  )
}

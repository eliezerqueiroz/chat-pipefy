import { useEffect, useRef } from 'react'
import { MessageSquare, Sparkles } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { MessageBubble } from './MessageBubble'
import { ChatInput } from './ChatInput'

export function ChatPanel() {
  const { activeSession, isStreaming } = useChatStore()
  const session = activeSession()
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom on new messages or streaming tokens
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [session?.messages.length, isStreaming])

  return (
    <main className="flex-1 flex flex-col h-full min-w-0">
      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {!session ? (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
            <div className="p-4 rounded-2xl bg-brand-500/10 border border-brand-500/20">
              <MessageSquare className="w-8 h-8 text-brand-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-200">No session selected</h2>
              <p className="text-sm text-gray-500 mt-1">
                Create a new chat session from the top bar to get started.
              </p>
            </div>
          </div>
        ) : session.messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
            <div className="p-4 rounded-2xl bg-brand-500/10 border border-brand-500/20">
              <Sparkles className="w-8 h-8 text-brand-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-200">Ready to answer</h2>
              <p className="text-sm text-gray-500 mt-1 max-w-md">
                Upload documents on the left, then ask anything about their content.
                Responses are grounded in your documents with source citations.
              </p>
            </div>
          </div>
        ) : (
          <>
            {session.messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput />
    </main>
  )
}

import type { Message } from '../../types'
import { SourcesDrawer } from './SourcesDrawer'
import { Bot, User } from 'lucide-react'

interface Props {
  message: Message
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 message-enter ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold
          ${isUser
            ? 'bg-brand-500 text-white'
            : 'bg-surface-600 border border-surface-500 text-gray-300'
          }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[80%] space-y-1 ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap break-words
            ${isUser
              ? 'bg-brand-500 text-white rounded-tr-sm'
              : 'bg-surface-700 text-gray-100 rounded-tl-sm border border-surface-600'
            }
            ${message.isStreaming ? 'typing-cursor' : ''}
          `}
        >
          {message.content || (message.isStreaming ? '' : '…')}
        </div>

        {/* Timestamp */}
        <span className="text-xs text-gray-600 px-1">
          {new Date(message.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
        </span>

        {/* Sources (assistant only) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full px-1">
            <SourcesDrawer sources={message.sources} />
          </div>
        )}
      </div>
    </div>
  )
}

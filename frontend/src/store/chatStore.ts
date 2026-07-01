/**
 * Zustand store for chat session management.
 * Handles multiple named sessions, message history, and streaming state.
 * Sessions are persisted to localStorage for continuity across page reloads.
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ChatSession, Message, Source } from '../types'
import { streamChat } from '../api/client'

function generateId(): string {
  return crypto.randomUUID()
}

function createSession(name?: string): ChatSession {
  return {
    id: generateId(),
    name: name || `Chat ${new Date().toLocaleTimeString()}`,
    createdAt: new Date(),
    messages: [],
  }
}

interface ChatState {
  sessions: ChatSession[]
  activeSessionId: string | null
  isStreaming: boolean

  // Getters
  activeSession: () => ChatSession | undefined

  // Session management
  createNewSession: (name?: string) => void
  renameSession: (sessionId: string, name: string) => void
  deleteSession: (sessionId: string) => void
  setActiveSession: (sessionId: string) => void

  // Messaging
  sendMessage: (question: string) => Promise<void>
  clearMessages: (sessionId: string) => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      sessions: [],
      activeSessionId: null,
      isStreaming: false,

      activeSession: () => {
        const { sessions, activeSessionId } = get()
        return sessions.find((s) => s.id === activeSessionId)
      },

      createNewSession: (name?: string) => {
        const session = createSession(name)
        set((s) => ({
          sessions: [session, ...s.sessions],
          activeSessionId: session.id,
        }))
      },

      renameSession: (sessionId, name) => {
        set((s) => ({
          sessions: s.sessions.map((sess) =>
            sess.id === sessionId ? { ...sess, name } : sess
          ),
        }))
      },

      deleteSession: (sessionId) => {
        set((s) => {
          const remaining = s.sessions.filter((sess) => sess.id !== sessionId)
          return {
            sessions: remaining,
            activeSessionId:
              s.activeSessionId === sessionId
                ? (remaining[0]?.id ?? null)
                : s.activeSessionId,
          }
        })
      },

      setActiveSession: (sessionId) => set({ activeSessionId: sessionId }),

      sendMessage: async (question: string) => {
        const { activeSessionId, sessions } = get()
        if (!activeSessionId || get().isStreaming) return

        const userMessage: Message = {
          id: generateId(),
          role: 'user',
          content: question,
          timestamp: new Date(),
        }

        const assistantId = generateId()
        const assistantMessage: Message = {
          id: assistantId,
          role: 'assistant',
          content: '',
          isStreaming: true,
          timestamp: new Date(),
        }

        // Add user message and a placeholder assistant message
        set((s) => ({
          isStreaming: true,
          sessions: s.sessions.map((sess) =>
            sess.id === activeSessionId
              ? { ...sess, messages: [...sess.messages, userMessage, assistantMessage] }
              : sess
          ),
        }))

        const updateAssistant = (update: Partial<Message>) => {
          set((s) => ({
            sessions: s.sessions.map((sess) =>
              sess.id === activeSessionId
                ? {
                    ...sess,
                    messages: sess.messages.map((m) =>
                      m.id === assistantId ? { ...m, ...update } : m
                    ),
                  }
                : sess
            ),
          }))
        }

        streamChat(
          activeSessionId,
          question,
          // onToken
          (token) => {
            set((s) => ({
              sessions: s.sessions.map((sess) =>
                sess.id === activeSessionId
                  ? {
                      ...sess,
                      messages: sess.messages.map((m) =>
                        m.id === assistantId
                          ? { ...m, content: m.content + token }
                          : m
                      ),
                    }
                  : sess
              ),
            }))
          },
          // onSources
          (sources: Source[]) => updateAssistant({ sources }),
          // onDone
          () => {
            updateAssistant({ isStreaming: false })
            set({ isStreaming: false })
          },
          // onError
          (err) => {
            updateAssistant({
              content: `⚠️ Error: ${err.message}`,
              isStreaming: false,
            })
            set({ isStreaming: false })
          }
        )
      },

      clearMessages: (sessionId) => {
        set((s) => ({
          sessions: s.sessions.map((sess) =>
            sess.id === sessionId ? { ...sess, messages: [] } : sess
          ),
        }))
      },
    }),
    {
      name: 'chat-pipefy-sessions',
      partialize: (s) => ({ sessions: s.sessions, activeSessionId: s.activeSessionId }),
    }
  )
)

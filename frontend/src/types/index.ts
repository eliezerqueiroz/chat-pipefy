/** Shared TypeScript interfaces for the entire frontend application. */

export interface Document {
  file_id: string
  name: string
  uploaded_at: string
  chunks: number
}

export interface UploadResponse {
  file_id: string
  name: string
  chunks_indexed: number
  status: string
}

export interface Source {
  content: string
  source: string
  chunk_index: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  isStreaming?: boolean
  timestamp: Date
}

export interface ChatSession {
  id: string
  name: string
  createdAt: Date
  messages: Message[]
}

export interface HealthStatus {
  status: string
  redis: string
}

/** SSE event types received from the streaming /chat endpoint */
export type SSEEvent =
  | { type: 'token'; content: string }
  | { type: 'sources'; data: Source[] }
  | { type: 'done' }

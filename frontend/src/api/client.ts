/**
 * Axios API client with typed methods for all backend endpoints.
 * Base URL is configured from the VITE_API_URL environment variable.
 */

import axios from 'axios'
import type { Document, UploadResponse, HealthStatus } from '../types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30_000,
})

/** Add response interceptor for global error logging */
api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('[API Error]', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

/** Upload a file for ingestion into the vector store */
export async function uploadDocument(file: File): Promise<UploadResponse> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<UploadResponse>('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

/** List all indexed documents */
export async function listDocuments(): Promise<Document[]> {
  const { data } = await api.get<Document[]>('/documents')
  return data
}

/** Delete a document and its vector chunks */
export async function deleteDocument(fileId: string): Promise<void> {
  await api.delete(`/documents/${fileId}`)
}

/** Check API and Redis health */
export async function getHealth(): Promise<HealthStatus> {
  const { data } = await api.get<HealthStatus>('/health')
  return data
}

/** Stream chat response via native fetch + ReadableStream (SSE) */
export function streamChat(
  sessionId: string,
  question: string,
  onToken: (token: string) => void,
  onSources: (sources: import('../types').Source[]) => void,
  onDone: () => void,
  onError: (err: Error) => void
): AbortController {
  const controller = new AbortController()

  fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            if (event.type === 'token') onToken(event.content)
            else if (event.type === 'sources') onSources(event.data)
            else if (event.type === 'done') onDone()
          } catch {
            // skip malformed lines
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError(err)
    })

  return controller
}

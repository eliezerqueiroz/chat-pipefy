/**
 * Zustand store for document management.
 * Handles listing, uploading, and deleting indexed documents.
 */

import { create } from 'zustand'
import type { Document } from '../types'
import { deleteDocument, listDocuments, uploadDocument } from '../api/client'

interface DocumentState {
  documents: Document[]
  isLoading: boolean
  isUploading: boolean
  uploadProgress: number
  error: string | null

  fetchDocuments: () => Promise<void>
  uploadFile: (file: File, onProgress?: (pct: number) => void) => Promise<void>
  removeDocument: (fileId: string) => Promise<void>
  clearError: () => void
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  isLoading: false,
  isUploading: false,
  uploadProgress: 0,
  error: null,

  fetchDocuments: async () => {
    set({ isLoading: true, error: null })
    try {
      const docs = await listDocuments()
      set({ documents: docs })
    } catch (err: any) {
      set({ error: err?.response?.data?.detail || 'Failed to fetch documents.' })
    } finally {
      set({ isLoading: false })
    }
  },

  uploadFile: async (file: File) => {
    set({ isUploading: true, uploadProgress: 0, error: null })
    try {
      // Simulate progress (real progress requires XMLHttpRequest)
      const progressInterval = setInterval(() => {
        set((s) => ({ uploadProgress: Math.min(s.uploadProgress + 15, 85) }))
      }, 200)

      await uploadDocument(file)
      clearInterval(progressInterval)
      set({ uploadProgress: 100 })

      // Refresh document list
      await get().fetchDocuments()
    } catch (err: any) {
      set({ error: err?.response?.data?.detail || 'Upload failed. Check the file format.' })
    } finally {
      setTimeout(() => set({ isUploading: false, uploadProgress: 0 }), 600)
    }
  },

  removeDocument: async (fileId: string) => {
    try {
      await deleteDocument(fileId)
      set((s) => ({ documents: s.documents.filter((d) => d.file_id !== fileId) }))
    } catch (err: any) {
      set({ error: err?.response?.data?.detail || 'Failed to delete document.' })
    }
  },

  clearError: () => set({ error: null }),
}))

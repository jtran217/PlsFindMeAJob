import { useState, useCallback } from 'react'
import type { Resume } from '../types/Resume'
import { createEmptyResume } from '../types/Resume'

interface UseResumeReturn {
  resume: Resume | null
  loading: boolean
  saving: boolean
  error: string | null
  loadResume: () => Promise<void>
  saveResume: (data: Resume) => Promise<boolean>
  clearError: () => void
}

export function useResume(): UseResumeReturn {
  const [resume, setResume] = useState<Resume | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadResume = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/resume')
      if (response.ok) {
        const data: Resume = await response.json()
        setResume(data)
      } else if (response.status === 404) {
        // No resume exists yet — start with an empty one
        setResume(createEmptyResume())
      } else {
        throw new Error(`Failed to load resume: ${response.status}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resume')
      // Fall back to empty resume so the UI is never blocked
      setResume(createEmptyResume())
    } finally {
      setLoading(false)
    }
  }, [])

  const saveResume = useCallback(async (data: Resume): Promise<boolean> => {
    setSaving(true)
    setError(null)
    try {
      const response = await fetch('/api/resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (response.ok) {
        setResume(data)
        return true
      } else {
        throw new Error(`Failed to save resume: ${response.status}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save resume')
      return false
    } finally {
      setSaving(false)
    }
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return { resume, loading, saving, error, loadResume, saveResume, clearError }
}

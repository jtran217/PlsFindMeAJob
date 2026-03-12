import { useState, useCallback } from 'react'
import type { OptimizedResume } from '../types/Resume'

interface UseResumeVersionsReturn {
  versions: string[]
  currentVersion: OptimizedResume | null
  loading: boolean
  error: string | null
  listVersions: () => Promise<void>
  getVersion: (jobId: string) => Promise<OptimizedResume | null>
  clearError: () => void
}

export function useResumeVersions(): UseResumeVersionsReturn {
  const [versions, setVersions] = useState<string[]>([])
  const [currentVersion, setCurrentVersion] = useState<OptimizedResume | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const listVersions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/resume/versions')
      if (!response.ok) {
        throw new Error(`Failed to list versions: ${response.status}`)
      }
      const data: { versions: string[] } = await response.json()
      setVersions(data.versions)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to list resume versions')
    } finally {
      setLoading(false)
    }
  }, [])

  const getVersion = useCallback(async (jobId: string): Promise<OptimizedResume | null> => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/resume/versions/${jobId}`)
      if (response.status === 404) {
        setCurrentVersion(null)
        return null
      }
      if (!response.ok) {
        throw new Error(`Failed to load version: ${response.status}`)
      }
      const version: OptimizedResume = await response.json()
      setCurrentVersion(version)
      return version
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resume version')
      return null
    } finally {
      setLoading(false)
    }
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return { versions, currentVersion, loading, error, listVersions, getVersion, clearError }
}

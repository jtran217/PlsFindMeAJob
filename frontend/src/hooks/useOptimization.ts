import { useState, useCallback } from 'react'
import type { JobAnalysisResult, OptimizedContent } from '../types/Resume'

interface UseOptimizationReturn {
  analysisResult: JobAnalysisResult | null
  optimizedContent: OptimizedContent | null
  analyzing: boolean
  optimizing: boolean
  error: string | null
  analyzeJob: (jobId: string) => Promise<JobAnalysisResult | null>
  optimizeResume: (
    jobId: string,
    selectedExperiences: string[],
    selectedProjects: string[]
  ) => Promise<OptimizedContent | null>
  clearError: () => void
  resetOptimization: () => void
}

export function useOptimization(): UseOptimizationReturn {
  const [analysisResult, setAnalysisResult] = useState<JobAnalysisResult | null>(null)
  const [optimizedContent, setOptimizedContent] = useState<OptimizedContent | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyzeJob = useCallback(async (jobId: string): Promise<JobAnalysisResult | null> => {
    setAnalyzing(true)
    setError(null)
    try {
      const response = await fetch(`/api/resume/analyze/${jobId}`, {
        method: 'POST',
      })
      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail ?? `Analysis failed: ${response.status}`)
      }
      const result: JobAnalysisResult = await response.json()
      setAnalysisResult(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Job analysis failed')
      return null
    } finally {
      setAnalyzing(false)
    }
  }, [])

  const optimizeResume = useCallback(
    async (
      jobId: string,
      selectedExperiences: string[],
      selectedProjects: string[]
    ): Promise<OptimizedContent | null> => {
      setOptimizing(true)
      setError(null)
      try {
        const response = await fetch(`/api/resume/optimize/${jobId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            selected_experiences: selectedExperiences,
            selected_projects: selectedProjects,
          }),
        })
        if (!response.ok) {
          const body = await response.json().catch(() => ({}))
          throw new Error(body.detail ?? `Optimization failed: ${response.status}`)
        }
        const content: OptimizedContent = await response.json()
        setOptimizedContent(content)
        return content
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Resume optimization failed')
        return null
      } finally {
        setOptimizing(false)
      }
    },
    []
  )

  const clearError = useCallback(() => setError(null), [])

  const resetOptimization = useCallback(() => {
    setAnalysisResult(null)
    setOptimizedContent(null)
    setError(null)
  }, [])

  return {
    analysisResult,
    optimizedContent,
    analyzing,
    optimizing,
    error,
    analyzeJob,
    optimizeResume,
    clearError,
    resetOptimization,
  }
}

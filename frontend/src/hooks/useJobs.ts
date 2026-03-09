import { useState, useEffect } from 'react'
import type { Job } from '../types/Job'

export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchJobs() {
      setLoading(true)
      setError(null)
      
      try {
        const response = await fetch('http://localhost:8000/api/jobs')

        if (!response.ok) {
          throw new Error(`Failed to fetch jobs: ${response.status}`)
        }

        const data = await response.json()
        setJobs(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred')
      } finally {
        setLoading(false)
      }
    }

    fetchJobs()
  }, [])

  return { jobs, loading, error }
}

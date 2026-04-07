import { useState, useEffect, useCallback } from 'react'
import type { Job } from '../types/Job'

const PAGE_SIZE = 20

interface PaginatedJobsResponse {
  items: Job[]
  total: number
  page: number
  page_size: number
  total_pages: number
  counts: { ready: number; applied: number; all: number }
}

export function useJobs(statusFilter?: string) {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [counts, setCounts] = useState({ ready: 0, applied: 0, all: 0 })

  const fetchJobs = useCallback(async (p: number) => {
    setLoading(true)
    setError(null)
    try {
      const url = `/api/jobs?page=${p}&page_size=${PAGE_SIZE}${statusFilter ? `&status=${statusFilter}` : ''}`
      const response = await fetch(url)
      if (!response.ok) throw new Error(`Failed to fetch jobs: ${response.status}`)
      const data: PaginatedJobsResponse = await response.json()
      setJobs(data.items)
      setTotal(data.total)
      setTotalPages(data.total_pages)
      setCounts(data.counts)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  const refreshJobs = useCallback(() => {
    setPage(1)
    fetchJobs(1)
  }, [fetchJobs])

  const goToPage = useCallback((p: number) => {
    setPage(p)
    fetchJobs(p)
  }, [fetchJobs])

  const deleteJob = useCallback(async (jobId: string) => {
    const response = await fetch(`/api/jobs/${jobId}`, { method: 'DELETE' })
    if (!response.ok) throw new Error(`Failed to delete job: ${response.status}`)
    setJobs(prev => prev.filter(j => j.id !== jobId))
    setTotal(prev => {
      const newTotal = prev - 1
      setTotalPages(Math.ceil(newTotal / PAGE_SIZE) || 1)
      return newTotal
    })
  }, [])

  const deleteAllJobs = useCallback(async () => {
    const response = await fetch('/api/jobs', { method: 'DELETE' })
    if (!response.ok) throw new Error(`Failed to delete all jobs: ${response.status}`)
    setJobs([])
    setTotal(0)
    setTotalPages(1)
    setCounts({ ready: 0, applied: 0, all: 0 })
  }, [])

  const updateJobStatus = useCallback(async (jobId: string, status: string) => {
    const response = await fetch(`/api/jobs/${jobId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    if (!response.ok) throw new Error(`Failed to update job status: ${response.status}`)
    setJobs(prev => prev.map(j => j.id === jobId ? { ...j, status } : j))
  }, [])

  // Reset to page 1 and refetch whenever the filter changes
  useEffect(() => {
    setPage(1)
    fetchJobs(1)
  }, [fetchJobs])

  return { jobs, loading, error, page, totalPages, total, counts, goToPage, refreshJobs, deleteJob, deleteAllJobs, updateJobStatus }
}

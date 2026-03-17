export type JobSite = 'indeed' | 'linkedin' | 'glassdoor' | 'zip_recruiter'

export interface ScraperSettings {
  search_term: string
  location: string
  interval_hours: number
  results_wanted: number
  hours_old: number
  sites: JobSite[]
  enabled: boolean
}

export interface ScraperStatus {
  last_run: string | null
  last_run_jobs_found: number
  last_run_jobs_added: number
  is_running: boolean
  next_run: string | null
  enabled: boolean
}

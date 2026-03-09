export interface Job {
  id: string
  site: string | null
  job_url: string | null
  job_url_direct: string | null
  title: string | null
  company: string | null
  location: string | null
  date_posted: string | null
  job_type: string | null
  is_remote: number
  description: string | null
  company_url: string | null
  company_url_direct: string | null
  skills: string | null
  experience_range: string | null
  status: string
}

/**
 * TypeScript interfaces for the Resume Optimization system.
 * Mirrors the backend Pydantic models in backend/app/models/resume.py exactly.
 */

// ---------------------------------------------------------------------------
// Core resume data structures
// ---------------------------------------------------------------------------

export interface PersonalInfo {
  name: string
  phone: string
  email: string
  linkedin: string
  github: string
}

export interface Education {
  id: string
  institution: string
  location: string
  degree: string
  duration: string
}

export interface TechnicalSkills {
  languages: string[]
  frameworks: string[]
  developer_tools: string[]
  libraries: string[]
}

export interface BulletPoint {
  id: string
  text: string
  keywords: string[]
  category: string
}

export interface Experience {
  id: string
  title: string
  company: string
  location: string
  duration: string
  bullet_points: BulletPoint[]
  /** Aggregated and deduplicated keywords from all bullet points (server-computed). */
  overall_keywords: readonly string[]
  relevance_score: number
}

export interface Project {
  id: string
  name: string
  technologies: string
  duration: string
  bullet_points: BulletPoint[]
  /** Aggregated and deduplicated keywords from all bullet points (server-computed). */
  overall_keywords: readonly string[]
  relevance_score: number
}

export interface Resume {
  personal_info: PersonalInfo
  education: Education[]
  technical_skills: TechnicalSkills
  experiences: Experience[]
  projects: Project[]
}

// ---------------------------------------------------------------------------
// Optimized / versioned resume structures
// ---------------------------------------------------------------------------

export interface OptimizedBullet {
  bullet_id: string
  original: string
  optimized: string
}

export interface OptimizedExperienceContent {
  optimized_bullet_points: OptimizedBullet[]
}

export interface OptimizedProjectContent {
  optimized_bullet_points: OptimizedBullet[]
}

export interface OptimizedContent {
  /** Keyed by experience id */
  experiences: Record<string, OptimizedExperienceContent>
  /** Keyed by project id */
  projects: Record<string, OptimizedProjectContent>
}

export interface OptimizedResume {
  job_id: string
  generated_at: string
  selected_experiences: string[]
  selected_projects: string[]
  optimized_content: OptimizedContent
}

// ---------------------------------------------------------------------------
// Job analysis structures
// ---------------------------------------------------------------------------

export interface JobAnalysis {
  job_id: string
  keywords: string[]
  technologies: string[]
  job_title: string
  company: string
}

export interface JobAnalysisResult {
  job_analysis: JobAnalysis
  ranked_experiences: Experience[]
  ranked_projects: Project[]
}

// ---------------------------------------------------------------------------
// Factory helpers
// ---------------------------------------------------------------------------

export function createEmptyResume(): Resume {
  return {
    personal_info: {
      name: '',
      phone: '',
      email: '',
      linkedin: '',
      github: '',
    },
    education: [],
    technical_skills: {
      languages: [],
      frameworks: [],
      developer_tools: [],
      libraries: [],
    },
    experiences: [],
    projects: [],
  }
}

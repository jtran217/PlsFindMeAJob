/**
 * Enhanced hook for managing resume data with the new resume optimization format.
 * Provides comprehensive functionality for the new resume system.
 */
import { useState, useCallback, useEffect } from 'react'
import type { 
  Resume,
  EnhancedBasics,
  ExperienceItem,
  EducationItem,
  ProjectItem,
  SkillItem,
  ProfileItem,
  LanguageItem,
  CertificationItem,
  AwardItem,
  InterestItem
} from '../types/resume'
import { 
  createExperienceItem,
  createEducationItem,
  createProjectItem,
  createSkillItem,
  createProfileItem,
  createLanguageItem,
  createCertificationItem,
  createAwardItem,
  createInterestItem,
  defaultWebsite
} from '../types/resume'

interface UseResumeOptions {
  autoMigrate?: boolean
  apiVersion?: 'v2'  // Future-proof for different API versions
}

interface UseResumeReturn {
  resume: Resume | null
  loading: boolean
  saving: boolean
  error: string | null
  validationErrors: Record<string, string> | null
  
  // Main operations
  loadResume: () => Promise<void>
  saveResume: () => Promise<boolean>
  migrateProfile: () => Promise<boolean>
  validateResume: () => Promise<boolean>
  
  // Basic info operations
  updateBasics: (basics: Partial<EnhancedBasics>) => void
  updateSummary: (content: string) => void
  
  // Experience operations
  addExperience: () => void
  updateExperience: (id: string, updates: Partial<ExperienceItem>) => void
  removeExperience: (id: string) => void
  
  // Education operations
  addEducation: () => void
  updateEducation: (id: string, updates: Partial<EducationItem>) => void
  removeEducation: (id: string) => void
  
  // Project operations
  addProject: () => void
  updateProject: (id: string, updates: Partial<ProjectItem>) => void
  removeProject: (id: string) => void
  
  // Skill operations
  addSkill: () => void
  updateSkill: (id: string, updates: Partial<SkillItem>) => void
  removeSkill: (id: string) => void
  
  // Profile operations
  addProfile: () => void
  updateProfile: (id: string, updates: Partial<ProfileItem>) => void
  removeProfile: (id: string) => void
  
  // Language operations
  addLanguage: () => void
  updateLanguage: (id: string, updates: Partial<LanguageItem>) => void
  removeLanguage: (id: string) => void
  
  // Certification operations
  addCertification: () => void
  updateCertification: (id: string, updates: Partial<CertificationItem>) => void
  removeCertification: (id: string) => void
  
  // Award operations
  addAward: () => void
  updateAward: (id: string, updates: Partial<AwardItem>) => void
  removeAward: (id: string) => void
  
  // Interest operations
  addInterest: () => void
  updateInterest: (id: string, updates: Partial<InterestItem>) => void
  removeInterest: (id: string) => void
  
  // Section management
  updateSectionVisibility: (section: string, hidden: boolean) => void
  
  // Utility operations
  clearErrors: () => void
  resetResume: () => void
}

const API_BASE_URL = 'http://localhost:8000/api/v2'

// Default resume structure
const createDefaultResume = (): Resume => ({
  name: 'My Resume',
  slug: 'my-resume',
  tags: ['Technology'],
  data: {
    picture: {
      hidden: true,
      url: '',
      size: 272,
      rotation: 0,
      aspectRatio: 1.0,
      borderRadius: 0,
      borderColor: '',
      borderWidth: 0,
      shadowColor: '',
      shadowWidth: 0
    },
    basics: {
      name: '',
      headline: '',
      email: '',
      phone: '',
      location: '',
      website: { ...defaultWebsite },
      customFields: []
    },
    summary: {
      title: 'Summary',
      columns: 1,
      hidden: false,
      content: ''
    },
    sections: {
      profiles: { title: 'Profiles', columns: 1, hidden: false, items: [] },
      experience: { title: 'Experience', columns: 1, hidden: false, items: [] },
      education: { title: 'Education', columns: 1, hidden: false, items: [] },
      projects: { title: 'Projects', columns: 1, hidden: false, items: [] },
      skills: { title: 'Skills', columns: 1, hidden: false, items: [] },
      languages: { title: 'Languages', columns: 1, hidden: true, items: [] },
      interests: { title: 'Interests', columns: 1, hidden: true, items: [] },
      awards: { title: 'Awards', columns: 1, hidden: true, items: [] },
      certifications: { title: 'Certifications', columns: 1, hidden: true, items: [] },
      publications: { title: 'Publications', columns: 1, hidden: true, items: [] },
      volunteer: { title: 'Volunteer', columns: 1, hidden: true, items: [] },
      references: { title: 'References', columns: 1, hidden: true, items: [] }
    },
    customSections: [],
    metadata: {
      template: 'azurill',
      layout: {
        sidebarWidth: 30,
        pages: [{
          fullWidth: false,
          main: ['summary', 'experience', 'education', 'projects', 'skills'],
          sidebar: ['basics', 'profiles']
        }]
      },
      css: { enabled: false, value: '' },
      page: {
        gapX: 16,
        gapY: 16,
        marginX: 16,
        marginY: 16,
        format: 'a4',
        locale: 'en',
        hideIcons: false
      },
      design: {
        level: { icon: '', type: 'hidden' },
        colors: { primary: '#000000', text: '#000000', background: '#ffffff' }
      },
      typography: {
        body: { fontFamily: '', fontWeights: ['400'], fontSize: 14, lineHeight: 1.5 },
        heading: { fontFamily: '', fontWeights: ['600'], fontSize: 16, lineHeight: 1.3 }
      },
      notes: ''
    }
  },
  isPublic: true
})

export const useResume = (options: UseResumeOptions = {}): UseResumeReturn => {
  const { autoMigrate = true } = options
  
  const [resume, setResume] = useState<Resume | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [saving, setSaving] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<Record<string, string> | null>(null)

  // Load resume from API
  const loadResume = useCallback(async (): Promise<void> => {
    try {
      setLoading(true)
      setError(null)
      
      const url = new URL(`${API_BASE_URL}/resume`)
      if (autoMigrate) {
        url.searchParams.set('auto_migrate', 'true')
      }
      
      const response = await fetch(url.toString())
      
      if (!response.ok) {
        throw new Error(`Failed to load resume: ${response.status}`)
      }
      
      const resumeData = await response.json() as Resume
      setResume(resumeData)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load resume'
      setError(errorMessage)
      console.error('Error loading resume:', err)
      
      // Set default resume on error
      setResume(createDefaultResume())
    } finally {
      setLoading(false)
    }
  }, [autoMigrate])

  // Save resume to API
  const saveResume = useCallback(async (): Promise<boolean> => {
    if (!resume) {
      setError('No resume data to save')
      return false
    }

    try {
      setSaving(true)
      setError(null)
      setValidationErrors(null)

      const response = await fetch(`${API_BASE_URL}/resume`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(resume)
      })

      const result = await response.json()

      if (!response.ok) {
        if (response.status === 422 && result.detail?.errors) {
          setValidationErrors(result.detail.errors)
          setError('Validation failed. Please check the form.')
        } else {
          setError(result.detail?.message || 'Failed to save resume')
        }
        return false
      }

      if (result.success) {
        return true
      } else {
        setError(result.message || 'Save failed')
        return false
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save resume'
      setError(errorMessage)
      console.error('Error saving resume:', err)
      return false
    } finally {
      setSaving(false)
    }
  }, [resume])

  // Migrate legacy profile
  const migrateProfile = useCallback(async (): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_BASE_URL}/resume/migrate`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`Migration failed: ${response.status}`)
      }

      const migratedResume = await response.json() as Resume
      setResume(migratedResume)
      return true

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Migration failed'
      setError(errorMessage)
      console.error('Error migrating profile:', err)
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  // Validate resume without saving
  const validateResume = useCallback(async (): Promise<boolean> => {
    if (!resume) return false

    try {
      setValidationErrors(null)

      const response = await fetch(`${API_BASE_URL}/resume/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(resume)
      })

      const result = await response.json()

      if (!response.ok && result.detail?.errors) {
        setValidationErrors(result.detail.errors)
        return false
      }

      return result.success || response.ok

    } catch (err) {
      console.error('Error validating resume:', err)
      return false
    }
  }, [resume])

  // Update basics
  const updateBasics = useCallback((updates: Partial<EnhancedBasics>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        basics: { ...prev.data.basics, ...updates }
      }
    } : null)
  }, [resume])

  // Update summary
  const updateSummary = useCallback((content: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        summary: { ...prev.data.summary, content }
      }
    } : null)
  }, [resume])

  // Experience operations
  const addExperience = useCallback((): void => {
    if (!resume) return

    const newItem = createExperienceItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          experience: {
            ...prev.data.sections.experience,
            items: [...prev.data.sections.experience.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateExperience = useCallback((id: string, updates: Partial<ExperienceItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          experience: {
            ...prev.data.sections.experience,
            items: prev.data.sections.experience.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeExperience = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          experience: {
            ...prev.data.sections.experience,
            items: prev.data.sections.experience.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Education operations
  const addEducation = useCallback((): void => {
    if (!resume) return

    const newItem = createEducationItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          education: {
            ...prev.data.sections.education,
            items: [...prev.data.sections.education.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateEducation = useCallback((id: string, updates: Partial<EducationItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          education: {
            ...prev.data.sections.education,
            items: prev.data.sections.education.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeEducation = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          education: {
            ...prev.data.sections.education,
            items: prev.data.sections.education.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Project operations
  const addProject = useCallback((): void => {
    if (!resume) return

    const newItem = createProjectItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          projects: {
            ...prev.data.sections.projects,
            items: [...prev.data.sections.projects.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateProject = useCallback((id: string, updates: Partial<ProjectItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          projects: {
            ...prev.data.sections.projects,
            items: prev.data.sections.projects.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeProject = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          projects: {
            ...prev.data.sections.projects,
            items: prev.data.sections.projects.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Skill operations
  const addSkill = useCallback((): void => {
    if (!resume) return

    const newItem = createSkillItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          skills: {
            ...prev.data.sections.skills,
            items: [...prev.data.sections.skills.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateSkill = useCallback((id: string, updates: Partial<SkillItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          skills: {
            ...prev.data.sections.skills,
            items: prev.data.sections.skills.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeSkill = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          skills: {
            ...prev.data.sections.skills,
            items: prev.data.sections.skills.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Profile operations  
  const addProfile = useCallback((): void => {
    if (!resume) return

    const newItem = createProfileItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          profiles: {
            ...prev.data.sections.profiles,
            items: [...prev.data.sections.profiles.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateProfile = useCallback((id: string, updates: Partial<ProfileItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          profiles: {
            ...prev.data.sections.profiles,
            items: prev.data.sections.profiles.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeProfile = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          profiles: {
            ...prev.data.sections.profiles,
            items: prev.data.sections.profiles.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Language operations
  const addLanguage = useCallback((): void => {
    if (!resume) return

    const newItem = createLanguageItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          languages: {
            ...prev.data.sections.languages,
            items: [...prev.data.sections.languages.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateLanguage = useCallback((id: string, updates: Partial<LanguageItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          languages: {
            ...prev.data.sections.languages,
            items: prev.data.sections.languages.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeLanguage = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          languages: {
            ...prev.data.sections.languages,
            items: prev.data.sections.languages.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Certification operations
  const addCertification = useCallback((): void => {
    if (!resume) return

    const newItem = createCertificationItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          certifications: {
            ...prev.data.sections.certifications,
            items: [...prev.data.sections.certifications.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateCertification = useCallback((id: string, updates: Partial<CertificationItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          certifications: {
            ...prev.data.sections.certifications,
            items: prev.data.sections.certifications.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeCertification = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          certifications: {
            ...prev.data.sections.certifications,
            items: prev.data.sections.certifications.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Award operations
  const addAward = useCallback((): void => {
    if (!resume) return

    const newItem = createAwardItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          awards: {
            ...prev.data.sections.awards,
            items: [...prev.data.sections.awards.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateAward = useCallback((id: string, updates: Partial<AwardItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          awards: {
            ...prev.data.sections.awards,
            items: prev.data.sections.awards.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeAward = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          awards: {
            ...prev.data.sections.awards,
            items: prev.data.sections.awards.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Interest operations
  const addInterest = useCallback((): void => {
    if (!resume) return

    const newItem = createInterestItem()
    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          interests: {
            ...prev.data.sections.interests,
            items: [...prev.data.sections.interests.items, newItem]
          }
        }
      }
    } : null)
  }, [resume])

  const updateInterest = useCallback((id: string, updates: Partial<InterestItem>): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          interests: {
            ...prev.data.sections.interests,
            items: prev.data.sections.interests.items.map(item =>
              item.id === id ? { ...item, ...updates } : item
            )
          }
        }
      }
    } : null)
  }, [resume])

  const removeInterest = useCallback((id: string): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          interests: {
            ...prev.data.sections.interests,
            items: prev.data.sections.interests.items.filter(item => item.id !== id)
          }
        }
      }
    } : null)
  }, [resume])

  // Section management
  const updateSectionVisibility = useCallback((section: string, hidden: boolean): void => {
    if (!resume) return

    setResume(prev => prev ? {
      ...prev,
      data: {
        ...prev.data,
        sections: {
          ...prev.data.sections,
          [section]: {
            ...prev.data.sections[section as keyof typeof prev.data.sections],
            hidden
          }
        }
      }
    } : null)
  }, [resume])

  // Utility operations
  const clearErrors = useCallback((): void => {
    setError(null)
    setValidationErrors(null)
  }, [])

  const resetResume = useCallback((): void => {
    setResume(createDefaultResume())
    clearErrors()
  }, [clearErrors])

  // Load resume on mount
  useEffect(() => {
    loadResume()
  }, [loadResume])

  return {
    resume,
    loading,
    saving,
    error,
    validationErrors,
    loadResume,
    saveResume,
    migrateProfile,
    validateResume,
    updateBasics,
    updateSummary,
    addExperience,
    updateExperience,
    removeExperience,
    addEducation,
    updateEducation,
    removeEducation,
    addProject,
    updateProject,
    removeProject,
    addSkill,
    updateSkill,
    removeSkill,
    addProfile,
    updateProfile,
    removeProfile,
    addLanguage,
    updateLanguage,
    removeLanguage,
    addCertification,
    updateCertification,
    removeCertification,
    addAward,
    updateAward,
    removeAward,
    addInterest,
    updateInterest,
    removeInterest,
    updateSectionVisibility,
    clearErrors,
    resetResume
  }
}
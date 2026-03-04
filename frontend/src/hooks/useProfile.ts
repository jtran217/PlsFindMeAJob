import { useState, useEffect, useCallback } from 'react';

type Basics = {
  name: string
  email: string
  phone: string
  linkedin?: string
  github?: string
}

type Experience = {
  company?: string
  position?: string
  start_date?: string
  end_date?: string
  location?: string
  bullets?: string[]
}

type Education = {
  institution?: string
  location?: string
  degree?: string
  expected_date?: string
  start_date?: string
  coursework?: string
}

type Project = {
  name?: string
  description?: string
}

type Profile = {
  basics: Basics
  experiences: Experience[]
  education: Education[]
  skills: string[]
  projects: Project[]
}

type ValidationErrors = {
  [key: string]: string
}

type SaveResult = {
  success: boolean
  message: string
  errors?: ValidationErrors
}

const emptyProfile: Profile = {
  basics: {
    name: "",
    email: "",
    phone: "",
    linkedin: "",
    github: ""
  },
  experiences: [],
  education: [],
  skills: [],
  projects: []
}

export function useProfile() {
  const [profile, setProfile] = useState<Profile>(emptyProfile);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  // New state for save operations
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<ValidationErrors>({});

  useEffect(() => {
    async function fetchProfile() {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch('http://localhost:8000/api/profile');
        
        if (!response.ok) {
          throw new Error(`Failed to load profile: ${response.statusText}`);
        }
        
        const data = await response.json();
        setProfile(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load profile';
        setError(errorMessage);
        console.error('Profile fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    
    fetchProfile();
  }, [])

  const validateProfile = useCallback((profileData: Profile): ValidationErrors => {
    const errors: ValidationErrors = {};
    
    // Basic validation
    if (!profileData.basics.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!profileData.basics.email.trim()) {
      errors.email = 'Email is required';
    } else {
      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(profileData.basics.email)) {
        errors.email = 'Please enter a valid email address';
      }
    }
    
    if (profileData.skills.length === 0) {
      errors.skills = 'At least one skill is required';
    }
    
    if (profileData.experiences.length === 0) {
      errors.experiences = 'At least one work experience is required';
    }
    
    if (profileData.education.length === 0) {
      errors.education = 'At least one education entry is required';
    }
    
    return errors;
  }, []);

  const clearFeedback = useCallback(() => {
    setSaveSuccess(null);
    setSaveError(null);
    setFieldErrors({});
  }, []);

  const saveProfile = useCallback(async (updatedProfile: Profile): Promise<SaveResult> => {
    // Clear previous feedback
    clearFeedback();
    
    // Validate before saving
    const validationErrors = validateProfile(updatedProfile);
    if (Object.keys(validationErrors).length > 0) {
      setFieldErrors(validationErrors);
      return {
        success: false,
        message: 'Please fix the validation errors',
        errors: validationErrors
      };
    }
    
    setIsSaving(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedProfile)
      });
      
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || `Save failed: ${response.statusText}`);
      }
      
      // Update local state with saved data
      setProfile(updatedProfile);
      setSaveSuccess('Profile saved successfully!');
      
      return {
        success: true,
        message: 'Profile saved successfully!'
      };
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save profile';
      setSaveError(errorMessage);
      console.error('Profile save error:', err);
      
      return {
        success: false,
        message: errorMessage
      };
    } finally {
      setIsSaving(false);
    }
  }, [validateProfile, clearFeedback]);

  return {
    // Profile data
    profile,
    setProfile,
    
    // Loading states
    loading,
    isSaving,
    
    // Error states
    error,
    saveError,
    fieldErrors,
    
    // Success states
    saveSuccess,
    
    // Actions
    saveProfile,
    clearFeedback,
    
    // Validation
    validateProfile,
  };
}

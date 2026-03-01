import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import defaultProfile from '../data/profileDefault.json'

type Basics = {
  name: string
  email: string
  phone: string
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
  degree?: string
  start_date?: string
  end_date?: string
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

const STORAGE_KEY = 'pfm_profile_v1'

function initials(name: string) {
  return name
    .split(' ')
    .map((s) => s[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

export default function Profile() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<Profile>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) return JSON.parse(raw)
    } catch (e) {
      // ignore
    }
    return (defaultProfile as unknown) as Profile
  })

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile))
    } catch (e) {
      // ignore
    }
  }, [profile])

  function updateBasics(partial: Partial<Basics>) {
    setProfile((p) => ({ ...p, basics: { ...p.basics, ...partial } }))
  }

  function updateSkills(text: string) {
    const arr = text
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    setProfile((p) => ({ ...p, skills: arr }))
  }

  return (
    <div className="relative">
      <button
        onClick={() => navigate('/profile')}
        title={profile.basics.name}
        className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-white/5 px-3 py-1 text-sm text-slate-200 hover:bg-white/10"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-sm font-semibold text-white">
          {initials(profile.basics.name || 'U')}
        </div>
        <span className="hidden sm:inline">{profile.basics.name}</span>
      </button>

      {/* Avatar navigates to profile page; modal editor moved to /profile */}
    </div>
  )
}

import { useMemo } from 'react'
import type { PersonalInfo } from '../../../types/Resume'

interface PersonalInfoSectionProps {
  data: PersonalInfo
  expanded: boolean
  onToggle: () => void
  onChange: (updated: PersonalInfo) => void
}

interface FieldError {
  email?: string
  phone?: string
  linkedin?: string
  github?: string
}

function validate(data: PersonalInfo): FieldError {
  const errors: FieldError = {}

  if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.email = 'Enter a valid email address'
  }

  if (data.phone && !/\d/.test(data.phone)) {
    errors.phone = 'Phone must contain at least one digit'
  }

  if (data.linkedin && !data.linkedin.includes('linkedin.com')) {
    errors.linkedin = 'URL should include linkedin.com'
  }

  if (data.github && !data.github.includes('github.com')) {
    errors.github = 'URL should include github.com'
  }

  return errors
}

function HeaderPreview({ data }: { data: PersonalInfo }) {
  const parts = useMemo(() => {
    return [data.phone, data.email, data.linkedin, data.github].filter(Boolean)
  }, [data.phone, data.email, data.linkedin, data.github])

  const hasContent = data.name || parts.length > 0

  if (!hasContent) return null

  return (
    <div className="mt-5 rounded-xl border border-slate-700/60 bg-slate-900/60 px-6 py-5 text-center shadow-inner">
      <p className="text-[11px] uppercase tracking-[0.25em] text-slate-500 mb-3">Preview</p>

      {data.name && (
        <p className="text-xl font-bold tracking-wide text-white">{data.name}</p>
      )}

      {parts.length > 0 && (
        <div className="mt-1.5 flex flex-wrap items-center justify-center gap-x-1.5 gap-y-1 text-xs text-slate-400">
          {parts.map((part, i) => (
            <span key={i} className="flex items-center gap-x-1.5">
              {i > 0 && <span className="text-slate-600 select-none">|</span>}
              <span className="truncate max-w-[220px]">{part}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

export function PersonalInfoSection({ data, expanded, onToggle, onChange }: PersonalInfoSectionProps) {
  const errors = useMemo(() => validate(data), [data])

  const fields: {
    key: keyof PersonalInfo
    label: string
    placeholder: string
    type?: string
  }[] = [
    { key: 'name',     label: 'Full Name',    placeholder: 'Jane Smith' },
    { key: 'phone',    label: 'Phone',        placeholder: '+1 (555) 000-0000' },
    { key: 'email',    label: 'Email',        placeholder: 'jane@example.com', type: 'email' },
    { key: 'linkedin', label: 'LinkedIn URL', placeholder: 'https://linkedin.com/in/...' },
    { key: 'github',   label: 'GitHub URL',   placeholder: 'https://github.com/...' },
  ]

  const hasErrors = Object.keys(errors).length > 0

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
      {/* Section header */}
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-6 py-4 text-left transition hover:bg-white/5"
      >
        <div className="flex items-center gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Resume</p>
            <p className="mt-0.5 text-base font-semibold text-white">Personal Information</p>
          </div>
          {hasErrors && !expanded && (
            <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-xs font-medium text-amber-400">
              {Object.keys(errors).length} warning{Object.keys(errors).length > 1 ? 's' : ''}
            </span>
          )}
        </div>
        <span className={`text-slate-400 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {/* Section body */}
      {expanded && (
        <div className="border-t border-slate-800/70 px-6 py-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {fields.map(({ key, label, placeholder, type }) => {
              const error = errors[key as keyof FieldError]
              return (
                <div key={key} className={key === 'name' ? 'sm:col-span-2' : ''}>
                  <label className="mb-1.5 block text-xs font-medium uppercase tracking-[0.15em] text-slate-400">
                    {label}
                  </label>
                  <input
                    type={type ?? 'text'}
                    value={data[key]}
                    placeholder={placeholder}
                    onChange={(e) => onChange({ ...data, [key]: e.target.value })}
                    className={`w-full rounded-xl border bg-white/5 px-4 py-2.5 text-sm text-white placeholder-slate-600 outline-none transition focus:ring-1 ${
                      error
                        ? 'border-amber-500/60 focus:border-amber-500/80 focus:ring-amber-500/20'
                        : 'border-slate-700/80 focus:border-indigo-500/60 focus:ring-indigo-500/30'
                    }`}
                  />
                  {error && (
                    <p className="mt-1 text-xs text-amber-400">{error}</p>
                  )}
                </div>
              )
            })}
          </div>

          <HeaderPreview data={data} />
        </div>
      )}
    </div>
  )
}

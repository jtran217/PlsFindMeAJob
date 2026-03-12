import type { PersonalInfo } from '../../../types/Resume'

interface PersonalInfoSectionProps {
  data: PersonalInfo
  expanded: boolean
  onToggle: () => void
  onChange: (updated: PersonalInfo) => void
}

export function PersonalInfoSection({ data, expanded, onToggle, onChange }: PersonalInfoSectionProps) {
  const fields: { key: keyof PersonalInfo; label: string; placeholder: string; type?: string }[] = [
    { key: 'name',     label: 'Full Name',       placeholder: 'Jane Smith' },
    { key: 'phone',    label: 'Phone',            placeholder: '+1 (555) 000-0000' },
    { key: 'email',    label: 'Email',            placeholder: 'jane@example.com', type: 'email' },
    { key: 'linkedin', label: 'LinkedIn URL',     placeholder: 'https://linkedin.com/in/...' },
    { key: 'github',   label: 'GitHub URL',       placeholder: 'https://github.com/...' },
  ]

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
      {/* Section header */}
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-6 py-4 text-left transition hover:bg-white/5"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Resume</p>
          <p className="mt-0.5 text-base font-semibold text-white">Personal Information</p>
        </div>
        <span className={`text-slate-400 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {/* Section body */}
      {expanded && (
        <div className="border-t border-slate-800/70 px-6 py-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {fields.map(({ key, label, placeholder, type }) => (
              <div key={key} className={key === 'name' ? 'sm:col-span-2' : ''}>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-[0.15em] text-slate-400">
                  {label}
                </label>
                <input
                  type={type ?? 'text'}
                  value={data[key]}
                  placeholder={placeholder}
                  onChange={(e) => onChange({ ...data, [key]: e.target.value })}
                  className="w-full rounded-xl border border-slate-700/80 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30"
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

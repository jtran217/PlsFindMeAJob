import { useState } from 'react'
import type { Education } from '../../../types/Resume'

interface EducationSectionProps {
  data: Education[]
  expanded: boolean
  onToggle: () => void
  onChange: (updated: Education[]) => void
}

function emptyEducation(): Education {
  return {
    id: crypto.randomUUID(),
    institution: '',
    location: '',
    degree: '',
    duration: '',
  }
}

export function EducationSection({ data, expanded, onToggle, onChange }: EducationSectionProps) {
  const [editingId, setEditingId] = useState<string | null>(null)

  const addEntry = () => {
    const entry = emptyEducation()
    onChange([...data, entry])
    setEditingId(entry.id)
  }

  const removeEntry = (id: string) => {
    onChange(data.filter((e) => e.id !== id))
    if (editingId === id) setEditingId(null)
  }

  const updateEntry = (id: string, field: keyof Omit<Education, 'id'>, value: string) => {
    onChange(data.map((e) => (e.id === id ? { ...e, [field]: value } : e)))
  }

  const fields: { key: keyof Omit<Education, 'id'>; label: string; placeholder: string }[] = [
    { key: 'institution', label: 'Institution',     placeholder: 'University of Example' },
    { key: 'location',    label: 'Location',        placeholder: 'City, State' },
    { key: 'degree',      label: 'Degree',          placeholder: 'B.S. Computer Science' },
    { key: 'duration',    label: 'Duration',        placeholder: 'Aug 2018 -- May 2022' },
  ]

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-6 py-4 text-left transition hover:bg-white/5"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Resume</p>
          <p className="mt-0.5 text-base font-semibold text-white">
            Education
            <span className="ml-2 rounded-lg bg-slate-800 px-2 py-0.5 text-xs font-semibold text-slate-300">
              {data.length}
            </span>
          </p>
        </div>
        <span className={`text-slate-400 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {expanded && (
        <div className="border-t border-slate-800/70 px-6 py-5 space-y-4">
          {data.map((entry) => (
            <div key={entry.id} className="rounded-xl border border-slate-800/70 bg-white/5 p-4">
              {editingId === entry.id ? (
                /* Edit form */
                <div className="space-y-3">
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {fields.map(({ key, label, placeholder }) => (
                      <div key={key}>
                        <label className="mb-1 block text-xs font-medium uppercase tracking-[0.15em] text-slate-400">
                          {label}
                        </label>
                        <input
                          type="text"
                          value={entry[key]}
                          placeholder={placeholder}
                          onChange={(e) => updateEntry(entry.id, key, e.target.value)}
                          className="w-full rounded-xl border border-slate-700/80 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30"
                        />
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-end">
                    <button
                      onClick={() => setEditingId(null)}
                      className="rounded-xl border border-indigo-500/50 bg-indigo-500/15 px-4 py-1.5 text-xs font-semibold text-white transition hover:bg-indigo-500/25"
                    >
                      Done
                    </button>
                  </div>
                </div>
              ) : (
                /* Read view */
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-white">
                      {entry.institution || <span className="italic text-slate-500">No institution</span>}
                    </p>
                    <p className="text-xs text-slate-400">{entry.degree}</p>
                    <p className="text-xs text-slate-500">{entry.location} {entry.location && entry.duration && '·'} {entry.duration}</p>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <button
                      onClick={() => setEditingId(entry.id)}
                      className="rounded-lg border border-slate-700 bg-white/5 px-3 py-1 text-xs text-slate-300 transition hover:border-slate-500 hover:text-white"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => removeEntry(entry.id)}
                      className="rounded-lg border border-red-900/50 bg-red-900/10 px-3 py-1 text-xs text-red-400 transition hover:bg-red-900/20"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}

          <button
            onClick={addEntry}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-700 py-3 text-sm text-slate-400 transition hover:border-indigo-500/50 hover:text-indigo-300"
          >
            <span className="text-lg leading-none">+</span> Add Education
          </button>
        </div>
      )}
    </div>
  )
}

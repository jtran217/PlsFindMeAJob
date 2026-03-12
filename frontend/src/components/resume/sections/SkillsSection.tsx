import { useState } from 'react'
import type { TechnicalSkills } from '../../../types/Resume'

interface SkillsSectionProps {
  data: TechnicalSkills
  expanded: boolean
  onToggle: () => void
  onChange: (updated: TechnicalSkills) => void
}

type SkillCategory = keyof TechnicalSkills

const CATEGORY_LABELS: Record<SkillCategory, string> = {
  languages:       'Languages',
  frameworks:      'Frameworks',
  developer_tools: 'Developer Tools',
  libraries:       'Libraries',
}

export function SkillsSection({ data, expanded, onToggle, onChange }: SkillsSectionProps) {
  const [inputs, setInputs] = useState<Record<SkillCategory, string>>({
    languages:       '',
    frameworks:      '',
    developer_tools: '',
    libraries:       '',
  })

  const addSkill = (category: SkillCategory) => {
    const value = inputs[category].trim()
    if (!value || data[category].includes(value)) return
    onChange({ ...data, [category]: [...data[category], value] })
    setInputs((prev) => ({ ...prev, [category]: '' }))
  }

  const removeSkill = (category: SkillCategory, skill: string) => {
    onChange({ ...data, [category]: data[category].filter((s) => s !== skill) })
  }

  const handleKeyDown = (e: React.KeyboardEvent, category: SkillCategory) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      addSkill(category)
    }
  }

  const totalSkills = Object.values(data).reduce((sum, arr) => sum + arr.length, 0)

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-6 py-4 text-left transition hover:bg-white/5"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Resume</p>
          <p className="mt-0.5 text-base font-semibold text-white">
            Technical Skills
            <span className="ml-2 rounded-lg bg-slate-800 px-2 py-0.5 text-xs font-semibold text-slate-300">
              {totalSkills}
            </span>
          </p>
        </div>
        <span className={`text-slate-400 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {expanded && (
        <div className="border-t border-slate-800/70 px-6 py-5 space-y-5">
          {(Object.keys(CATEGORY_LABELS) as SkillCategory[]).map((category) => (
            <div key={category}>
              <label className="mb-2 block text-xs font-medium uppercase tracking-[0.15em] text-slate-400">
                {CATEGORY_LABELS[category]}
              </label>

              {/* Tags */}
              <div className="mb-2 flex flex-wrap gap-2">
                {data[category].map((skill) => (
                  <span
                    key={skill}
                    className="flex items-center gap-1.5 rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-1 text-xs font-medium text-indigo-200"
                  >
                    {skill}
                    <button
                      onClick={() => removeSkill(category, skill)}
                      className="text-indigo-400 transition hover:text-red-400"
                      aria-label={`Remove ${skill}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
                {data[category].length === 0 && (
                  <span className="text-xs italic text-slate-600">No skills added yet</span>
                )}
              </div>

              {/* Add input */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputs[category]}
                  placeholder={`Add ${CATEGORY_LABELS[category].toLowerCase()}...`}
                  onChange={(e) => setInputs((prev) => ({ ...prev, [category]: e.target.value }))}
                  onKeyDown={(e) => handleKeyDown(e, category)}
                  className="flex-1 rounded-xl border border-slate-700/80 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30"
                />
                <button
                  onClick={() => addSkill(category)}
                  className="rounded-xl border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-300 transition hover:border-indigo-500/50 hover:text-white"
                >
                  Add
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

import { useState } from 'react'
import type { Project, BulletPoint } from '../../../types/Resume'

interface ProjectFormProps {
  project?: Project
  onSave: (project: Project) => void
  onCancel: () => void
}

function emptyBullet(): BulletPoint {
  return { id: crypto.randomUUID(), text: '', keywords: [], category: 'technical' }
}

function emptyProject(): Project {
  return {
    id: crypto.randomUUID(),
    name: '',
    technologies: '',
    duration: '',
    bullet_points: [emptyBullet()],
    overall_keywords: [],
    relevance_score: 0,
  }
}

export function ProjectForm({ project, onSave, onCancel }: ProjectFormProps) {
  const isNew = !project
  const [draft, setDraft] = useState<Project>(() =>
    project ? { ...project, bullet_points: project.bullet_points.map((b) => ({ ...b })) } : emptyProject()
  )
  const [bulletEditingId, setBulletEditingId] = useState<string | null>(
    isNew && draft.bullet_points.length > 0 ? draft.bullet_points[0].id : null
  )

  const updateField = (
    field: keyof Omit<Project, 'id' | 'bullet_points' | 'overall_keywords' | 'relevance_score'>,
    value: string
  ) => {
    setDraft((prev) => ({ ...prev, [field]: value }))
  }

  const updateBullet = (id: string, text: string) => {
    setDraft((prev) => ({
      ...prev,
      bullet_points: prev.bullet_points.map((b) => (b.id === id ? { ...b, text } : b)),
    }))
  }

  const addBullet = () => {
    const bullet = emptyBullet()
    setDraft((prev) => ({ ...prev, bullet_points: [...prev.bullet_points, bullet] }))
    setBulletEditingId(bullet.id)
  }

  const removeBullet = (id: string) => {
    setDraft((prev) => ({
      ...prev,
      bullet_points: prev.bullet_points.filter((b) => b.id !== id),
    }))
    if (bulletEditingId === id) setBulletEditingId(null)
  }

  const moveBullet = (id: string, direction: 'up' | 'down') => {
    setDraft((prev) => {
      const bullets = [...prev.bullet_points]
      const idx = bullets.findIndex((b) => b.id === id)
      if (direction === 'up' && idx > 0) {
        [bullets[idx - 1], bullets[idx]] = [bullets[idx], bullets[idx - 1]]
      } else if (direction === 'down' && idx < bullets.length - 1) {
        [bullets[idx], bullets[idx + 1]] = [bullets[idx + 1], bullets[idx]]
      }
      return { ...prev, bullet_points: bullets }
    })
  }

  const handleSave = () => {
    const cleaned = { ...draft, bullet_points: draft.bullet_points.filter((b) => b.text.trim()) }
    onSave(cleaned)
  }

  const topFields: {
    key: keyof Omit<Project, 'id' | 'bullet_points' | 'overall_keywords' | 'relevance_score'>
    label: string
    placeholder: string
    span?: boolean
  }[] = [
    { key: 'name',         label: 'Project Name',  placeholder: 'My Awesome Project', span: true },
    { key: 'technologies', label: 'Technologies',  placeholder: 'Python, React, PostgreSQL', span: true },
    { key: 'duration',     label: 'Duration',      placeholder: 'Jan 2024 -- Present' },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-800/80 bg-[#0b1228] shadow-2xl flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 pt-6 pb-4 border-b border-slate-800/70 shrink-0">
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
            {isNew ? 'Add' : 'Edit'}
          </p>
          <h2 className="mt-0.5 text-lg font-semibold text-white">Project</h2>
        </div>

        {/* Scrollable body */}
        <div className="overflow-y-auto px-6 py-5 space-y-5">
          {/* Top fields */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {topFields.map(({ key, label, placeholder, span }) => (
              <div key={key} className={span ? 'sm:col-span-2' : ''}>
                <label className="mb-1.5 block text-xs font-medium uppercase tracking-[0.15em] text-slate-400">
                  {label}
                </label>
                <input
                  type="text"
                  value={draft[key]}
                  placeholder={placeholder}
                  onChange={(e) => updateField(key, e.target.value)}
                  className="w-full rounded-xl border border-slate-700/80 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30"
                />
              </div>
            ))}
          </div>

          {/* Bullet points */}
          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="text-xs font-medium uppercase tracking-[0.15em] text-slate-400">
                Bullet Points
              </label>
              <span className="text-xs text-slate-600">
                {draft.bullet_points.length} bullet{draft.bullet_points.length !== 1 ? 's' : ''}
              </span>
            </div>

            <div className="space-y-2">
              {draft.bullet_points.map((bullet, idx) => (
                <div key={bullet.id} className="rounded-xl border border-slate-800/70 bg-white/5">
                  {bulletEditingId === bullet.id ? (
                    <div className="p-3">
                      <textarea
                        autoFocus
                        value={bullet.text}
                        placeholder="Describe what you built, its impact, or technologies used..."
                        onChange={(e) => updateBullet(bullet.id, e.target.value)}
                        rows={3}
                        className="w-full resize-none rounded-lg border border-slate-700/80 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30"
                      />
                      <div className="mt-2 flex justify-end">
                        <button
                          onClick={() => setBulletEditingId(null)}
                          className="rounded-lg border border-indigo-500/50 bg-indigo-500/15 px-3 py-1 text-xs font-semibold text-white transition hover:bg-indigo-500/25"
                        >
                          Done
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-start gap-2 p-3">
                      <span className="mt-0.5 shrink-0 text-xs text-slate-600 select-none w-4">
                        {idx + 1}.
                      </span>
                      <p
                        onClick={() => setBulletEditingId(bullet.id)}
                        className={`flex-1 cursor-text text-sm leading-relaxed ${bullet.text ? 'text-slate-200' : 'italic text-slate-600'}`}
                      >
                        {bullet.text || 'Click to add text...'}
                      </p>
                      <div className="flex shrink-0 items-center gap-1">
                        <button
                          onClick={() => moveBullet(bullet.id, 'up')}
                          disabled={idx === 0}
                          className="rounded px-1.5 py-0.5 text-xs text-slate-500 transition hover:text-slate-300 disabled:opacity-20"
                          title="Move up"
                        >
                          ↑
                        </button>
                        <button
                          onClick={() => moveBullet(bullet.id, 'down')}
                          disabled={idx === draft.bullet_points.length - 1}
                          className="rounded px-1.5 py-0.5 text-xs text-slate-500 transition hover:text-slate-300 disabled:opacity-20"
                          title="Move down"
                        >
                          ↓
                        </button>
                        <button
                          onClick={() => setBulletEditingId(bullet.id)}
                          className="rounded px-1.5 py-0.5 text-xs text-slate-400 transition hover:text-white"
                          title="Edit"
                        >
                          ✏
                        </button>
                        <button
                          onClick={() => removeBullet(bullet.id)}
                          className="rounded px-1.5 py-0.5 text-xs text-red-500/60 transition hover:text-red-400"
                          title="Remove"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              <button
                onClick={addBullet}
                className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-700 py-2.5 text-sm text-slate-400 transition hover:border-indigo-500/50 hover:text-indigo-300"
              >
                <span className="text-base leading-none">+</span> Add Bullet
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800/70 flex justify-end gap-3 shrink-0">
          <button
            onClick={onCancel}
            className="rounded-xl border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="rounded-xl border border-indigo-500/50 bg-indigo-500/15 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500/25 shadow-[0_8px_30px_rgba(79,70,229,0.2)]"
          >
            {isNew ? 'Add Project' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

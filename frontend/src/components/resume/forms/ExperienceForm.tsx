import type { Experience, BulletPoint } from '../../../types/Resume'

interface ExperienceFormProps {
  experience?: Experience
  onSave: (experience: Experience) => void
  onCancel: () => void
}

function emptyBullet(): BulletPoint {
  return { id: crypto.randomUUID(), text: '', keywords: [], category: 'technical' }
}

export function ExperienceForm({ experience, onSave, onCancel }: ExperienceFormProps) {
  const isNew = !experience

  // Full form logic implemented in Phase 3.
  // For now: a placeholder modal shell that signals intent.
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-xl rounded-2xl border border-slate-800/80 bg-[#0b1228] p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white">
          {isNew ? 'Add Experience' : 'Edit Experience'}
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Full experience editing is coming in Phase 3.
        </p>
        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onCancel}
            className="rounded-xl border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
          >
            Cancel
          </button>
          <button
            onClick={() =>
              onSave(
                experience ?? {
                  id: crypto.randomUUID(),
                  title: '',
                  company: '',
                  location: '',
                  duration: '',
                  bullet_points: [emptyBullet()],
                  overall_keywords: [],
                  relevance_score: 0,
                }
              )
            }
            className="rounded-xl border border-indigo-500/50 bg-indigo-500/15 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500/25"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

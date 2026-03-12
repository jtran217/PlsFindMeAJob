import type { BulletPoint } from '../../../types/Resume'

interface BulletPointFormProps {
  bullet?: BulletPoint
  onSave: (bullet: BulletPoint) => void
  onCancel: () => void
}

export function BulletPointForm({ bullet, onSave, onCancel }: BulletPointFormProps) {
  // Full inline editing logic implemented in Phase 3.
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-xl rounded-2xl border border-slate-800/80 bg-[#0b1228] p-6 shadow-2xl">
        <h2 className="text-lg font-semibold text-white">
          {bullet ? 'Edit Bullet Point' : 'Add Bullet Point'}
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Full bullet point editing is coming in Phase 3.
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
                bullet ?? {
                  id: crypto.randomUUID(),
                  text: '',
                  keywords: [],
                  category: 'technical',
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

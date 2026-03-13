import { useState } from 'react'
import type { Resume, OptimizedContent, OptimizedBullet } from '../../../types/Resume'
import type { Job } from '../../../types/Job'

interface OptimizationReviewProps {
  resume: Resume
  optimizedContent: OptimizedContent
  selectedExperienceIds: string[]
  selectedProjectIds: string[]
  selectedJob: Job | null
  onDone: (finalContent: OptimizedContent) => void
  onBack: () => void
}

interface BulletState {
  text: string
  accepted: boolean
  editing: boolean
}

type BulletStateMap = Record<string, BulletState> // keyed by bullet_id

function buildInitialBulletState(optimizedContent: OptimizedContent): BulletStateMap {
  const map: BulletStateMap = {}
  for (const expContent of Object.values(optimizedContent.experiences)) {
    for (const b of expContent.optimized_bullet_points) {
      map[b.bullet_id] = { text: b.optimized, accepted: false, editing: false }
    }
  }
  for (const projContent of Object.values(optimizedContent.projects)) {
    for (const b of projContent.optimized_bullet_points) {
      map[b.bullet_id] = { text: b.optimized, accepted: false, editing: false }
    }
  }
  return map
}

function buildFinalContent(
  optimizedContent: OptimizedContent,
  bulletStates: BulletStateMap
): OptimizedContent {
  const patchBullets = (bullets: OptimizedBullet[]): OptimizedBullet[] =>
    bullets.map((b) => ({
      ...b,
      optimized: bulletStates[b.bullet_id]?.text ?? b.optimized,
    }))

  return {
    experiences: Object.fromEntries(
      Object.entries(optimizedContent.experiences).map(([id, content]) => [
        id,
        { ...content, optimized_bullet_points: patchBullets(content.optimized_bullet_points) },
      ])
    ),
    projects: Object.fromEntries(
      Object.entries(optimizedContent.projects).map(([id, content]) => [
        id,
        { ...content, optimized_bullet_points: patchBullets(content.optimized_bullet_points) },
      ])
    ),
  }
}

function BulletRow({
  bullet,
  state,
  onChange,
  onAccept,
  onRevert,
  onToggleEdit,
}: {
  bullet: OptimizedBullet
  state: BulletState
  onChange: (text: string) => void
  onAccept: () => void
  onRevert: () => void
  onToggleEdit: () => void
}) {
  // True when the user has manually edited the AI-generated text.
  // Used to show the "Edited" label and the "↺ Revert to AI" button.
  const hasEdits = state.text !== bullet.optimized

  return (
    <div className={`rounded-xl border p-4 transition ${state.accepted ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-slate-800/70 bg-white/5'}`}>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {/* Original */}
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-[0.15em] text-slate-500">Original</p>
          <p className="text-sm leading-relaxed text-slate-400">{bullet.original}</p>
        </div>

        {/* Optimized */}
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-[0.15em] text-emerald-500/70">Optimized</p>
          {state.editing ? (
            <textarea
              autoFocus
              value={state.text}
              onChange={(e) => onChange(e.target.value)}
              rows={4}
              className="w-full resize-none rounded-lg border border-slate-700/80 bg-white/5 px-3 py-2 text-sm text-white placeholder-slate-600 outline-none transition focus:border-indigo-500/60 focus:ring-1 focus:ring-indigo-500/30"
            />
          ) : (
            <p className={`text-sm leading-relaxed ${state.accepted ? 'text-emerald-300' : 'text-white'}`}>
              {state.text}
            </p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {state.accepted ? (
          <>
            <span className="text-xs text-emerald-400 font-medium">✓ Accepted</span>
            <button
              onClick={onRevert}
              className="rounded-lg border border-slate-700 bg-white/5 px-2.5 py-1 text-xs text-slate-400 transition hover:text-white"
            >
              Undo
            </button>
          </>
        ) : (
          <>
            <button
              onClick={onAccept}
              className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-2.5 py-1 text-xs text-emerald-400 transition hover:bg-emerald-500/20"
            >
              ✓ Accept
            </button>
            <button
              onClick={onToggleEdit}
              className={`rounded-lg border px-2.5 py-1 text-xs transition ${
                state.editing
                  ? 'border-indigo-500/50 bg-indigo-500/15 text-white'
                  : 'border-slate-700 bg-white/5 text-slate-400 hover:text-white'
              }`}
            >
              {state.editing ? 'Done editing' : '✏ Edit'}
            </button>
            {hasEdits && (
              <button
                onClick={onRevert}
                className="rounded-lg border border-slate-700 bg-white/5 px-2.5 py-1 text-xs text-slate-500 transition hover:text-slate-300"
              >
                ↺ Revert to AI
              </button>
            )}
          </>
        )}
        {hasEdits && !state.editing && (
          <span className="ml-auto text-xs text-amber-400/70 italic">Edited</span>
        )}
      </div>
    </div>
  )
}

export function OptimizationReview({
  resume,
  optimizedContent,
  selectedExperienceIds,
  selectedProjectIds,
  selectedJob,
  onDone,
  onBack,
}: OptimizationReviewProps) {
  const [bulletStates, setBulletStates] = useState<BulletStateMap>(() =>
    buildInitialBulletState(optimizedContent)
  )

  const updateBullet = (bulletId: string, patch: Partial<BulletState>) => {
    setBulletStates((prev) => ({
      ...prev,
      [bulletId]: { ...prev[bulletId], ...patch },
    }))
  }

  const acceptAll = () => {
    setBulletStates((prev) => {
      const next = { ...prev }
      for (const id of Object.keys(next)) {
        next[id] = { ...next[id], accepted: true, editing: false }
      }
      return next
    })
  }

  const acceptedCount = Object.values(bulletStates).filter((s) => s.accepted).length
  const totalCount = Object.keys(bulletStates).length

  const selectedExperiences = resume.experiences.filter((e) => selectedExperienceIds.includes(e.id))
  const selectedProjects = resume.projects.filter((p) => selectedProjectIds.includes(p.id))

  const handleDone = () => {
    onDone(buildFinalContent(optimizedContent, bulletStates))
  }

  return (
    <div className="space-y-5">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          <span className="font-semibold text-white">{acceptedCount}</span> / {totalCount} bullets accepted
          {selectedJob ? ` for ${selectedJob.title}${selectedJob.company ? ` @ ${selectedJob.company}` : ''}` : ''}
        </p>
        <button
          onClick={acceptAll}
          className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400 transition hover:bg-emerald-500/20"
        >
          Accept All
        </button>
      </div>

      {/* Experiences */}
      {selectedExperiences.map((exp) => {
        const content = optimizedContent.experiences[exp.id]
        if (!content) return null
        return (
          <div key={exp.id}>
            <div className="mb-2">
              <p className="text-sm font-semibold text-white">{exp.title}</p>
              <p className="text-xs text-slate-400">
                {[exp.company, exp.location].filter(Boolean).join(' · ')}
                {exp.duration ? ` · ${exp.duration}` : ''}
              </p>
            </div>
            <div className="space-y-3">
              {content.optimized_bullet_points.map((bullet) => {
                const state = bulletStates[bullet.bullet_id]
                if (!state) return null
                return (
                  <BulletRow
                    key={bullet.bullet_id}
                    bullet={bullet}
                    state={state}
                    onChange={(text) => updateBullet(bullet.bullet_id, { text })}
                    onAccept={() => updateBullet(bullet.bullet_id, { accepted: true, editing: false })}
                    onRevert={() => updateBullet(bullet.bullet_id, { text: bullet.optimized, accepted: false, editing: false })}
                    onToggleEdit={() => updateBullet(bullet.bullet_id, { editing: !state.editing })}
                  />
                )
              })}
            </div>
          </div>
        )
      })}

      {/* Projects */}
      {selectedProjects.map((proj) => {
        const content = optimizedContent.projects[proj.id]
        if (!content) return null
        return (
          <div key={proj.id}>
            <div className="mb-2">
              <p className="text-sm font-semibold text-white">{proj.name}</p>
              {proj.technologies && <p className="text-xs text-indigo-300/70">{proj.technologies}</p>}
              {proj.duration && <p className="text-xs text-slate-500">{proj.duration}</p>}
            </div>
            <div className="space-y-3">
              {content.optimized_bullet_points.map((bullet) => {
                const state = bulletStates[bullet.bullet_id]
                if (!state) return null
                return (
                  <BulletRow
                    key={bullet.bullet_id}
                    bullet={bullet}
                    state={state}
                    onChange={(text) => updateBullet(bullet.bullet_id, { text })}
                    onAccept={() => updateBullet(bullet.bullet_id, { accepted: true, editing: false })}
                    onRevert={() => updateBullet(bullet.bullet_id, { text: bullet.optimized, accepted: false, editing: false })}
                    onToggleEdit={() => updateBullet(bullet.bullet_id, { editing: !state.editing })}
                  />
                )
              })}
            </div>
          </div>
        )
      })}

      {/* Navigation */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800/70">
        <button
          onClick={onBack}
          className="rounded-xl border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
        >
          ← Back
        </button>
        <button
          onClick={handleDone}
          className="rounded-xl border border-indigo-500/70 bg-indigo-500/15 px-4 py-2 text-sm font-semibold text-white shadow-[0_10px_40px_rgba(79,70,229,0.3)] transition hover:bg-indigo-500/25"
        >
          Generate PDF →
        </button>
      </div>
    </div>
  )
}

import { useState, useMemo } from 'react'
import type { JobAnalysisResult, Resume, Experience, Project } from '../../../types/Resume'
import type { Job } from '../../../types/Job'

interface ContentSelectorProps {
  analysisResult: JobAnalysisResult
  resume: Resume
  selectedJob: Job | null
  onConfirm: (experienceIds: string[], projectIds: string[]) => void
  optimizing: boolean
}

const MAX_SELECTIONS = 5

function ScoreBadge({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color =
    pct >= 60 ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400' :
    pct >= 30 ? 'border-amber-500/40 bg-amber-500/10 text-amber-400' :
                'border-slate-700 bg-white/5 text-slate-400'
  return (
    <span className={`rounded-lg border px-2 py-0.5 text-xs font-semibold tabular-nums ${color}`}>
      {pct}%
    </span>
  )
}

function ItemCard({
  title,
  subtitle,
  bullets,
  score,
  selected,
  onToggle,
  disabled,
}: {
  title: string
  subtitle: string
  bullets: string[]
  score: number
  selected: boolean
  onToggle: () => void
  disabled: boolean
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className={`rounded-xl border transition ${
        selected
          ? 'border-indigo-500/50 bg-indigo-500/8'
          : 'border-slate-800/70 bg-white/5'
      }`}
    >
      <div className="flex items-start gap-3 p-3">
        {/* Checkbox */}
        <button
          onClick={onToggle}
          disabled={disabled && !selected}
          className={`mt-0.5 h-4 w-4 shrink-0 rounded border transition ${
            selected
              ? 'border-indigo-500 bg-indigo-500'
              : disabled
              ? 'cursor-not-allowed border-slate-700 bg-white/5 opacity-40'
              : 'border-slate-600 bg-white/5 hover:border-indigo-400'
          }`}
          aria-label={selected ? 'Deselect' : 'Select'}
        >
          {selected && (
            <span className="flex items-center justify-center text-white text-xs leading-none">✓</span>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="text-sm font-semibold text-white leading-tight">
                {title || <em className="text-slate-500">Untitled</em>}
              </p>
              <p className="text-xs text-slate-400">{subtitle}</p>
            </div>
            <ScoreBadge score={score} />
          </div>

          {bullets.length > 0 && (
            <div className="mt-2">
              <ul className={`space-y-1 overflow-hidden ${expanded ? '' : 'max-h-12'}`}>
                {bullets.map((b, i) => (
                  <li key={i} className="text-xs text-slate-500 leading-relaxed">
                    • {b}
                  </li>
                ))}
              </ul>
              {bullets.length > 2 && (
                <button
                  onClick={() => setExpanded((p) => !p)}
                  className="mt-1 text-xs text-slate-600 transition hover:text-slate-400"
                >
                  {expanded ? 'Show less' : `+${bullets.length - 2} more`}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function SelectionColumn({
  label,
  selectedItems,
  availableItems,
  onToggle,
  atMax,
  renderTitle,
  renderSubtitle,
}: {
  label: string
  selectedItems: Array<Experience | Project>
  availableItems: Array<Experience | Project>
  onToggle: (id: string) => void
  atMax: boolean
  renderTitle: (item: Experience | Project) => string
  renderSubtitle: (item: Experience | Project) => string
}) {
  const totalCount = selectedItems.length + availableItems.length
  if (totalCount === 0) return null

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-[0.15em] text-slate-400">{label}</p>
        <span className="text-xs text-slate-500">{selectedItems.length} selected</span>
      </div>

      {selectedItems.length > 0 && (
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-2.5 space-y-2">
          <p className="text-xs font-medium text-emerald-500/70 px-1">Auto-Selected ({selectedItems.length})</p>
          {selectedItems.map((item) => (
            <ItemCard
              key={item.id}
              title={renderTitle(item)}
              subtitle={renderSubtitle(item)}
              bullets={'bullet_points' in item ? item.bullet_points.slice(0, 3).map((b) => b.text) : []}
              score={item.relevance_score}
              selected={true}
              onToggle={() => onToggle(item.id)}
              disabled={false}
            />
          ))}
        </div>
      )}

      {availableItems.length > 0 && (
        <div className="rounded-xl border border-slate-800/50 bg-white/[0.02] p-2.5 space-y-2">
          <p className="text-xs font-medium text-slate-600 px-1">Available</p>
          {availableItems.map((item) => (
            <ItemCard
              key={item.id}
              title={renderTitle(item)}
              subtitle={renderSubtitle(item)}
              bullets={'bullet_points' in item ? item.bullet_points.slice(0, 3).map((b) => b.text) : []}
              score={item.relevance_score}
              selected={false}
              onToggle={() => onToggle(item.id)}
              disabled={atMax}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function ContentSelector({
  analysisResult,
  resume: _resume,
  selectedJob,
  onConfirm,
  optimizing,
}: ContentSelectorProps) {
  const rankedExperiences: Experience[] = analysisResult.ranked_experiences
  const rankedProjects: Project[] = analysisResult.ranked_projects

  const initialSelected = useMemo(() => {
    const all = [
      ...rankedExperiences.map((e) => ({ id: e.id, type: 'exp' as const, score: e.relevance_score })),
      ...rankedProjects.map((p) => ({ id: p.id, type: 'proj' as const, score: p.relevance_score })),
    ].sort((a, b) => b.score - a.score)

    const top = all.slice(0, MAX_SELECTIONS)
    return {
      expIds: new Set(top.filter((x) => x.type === 'exp').map((x) => x.id)),
      projIds: new Set(top.filter((x) => x.type === 'proj').map((x) => x.id)),
    }
  }, [rankedExperiences, rankedProjects])

  const [selectedExpIds, setSelectedExpIds] = useState<Set<string>>(initialSelected.expIds)
  const [selectedProjIds, setSelectedProjIds] = useState<Set<string>>(initialSelected.projIds)

  const totalSelected = selectedExpIds.size + selectedProjIds.size
  const atMax = totalSelected >= MAX_SELECTIONS

  const toggleExp = (id: string) => {
    setSelectedExpIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) { next.delete(id) } else { next.add(id) }
      return next
    })
  }

  const toggleProj = (id: string) => {
    setSelectedProjIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) { next.delete(id) } else { next.add(id) }
      return next
    })
  }

  const handleReset = () => {
    setSelectedExpIds(initialSelected.expIds)
    setSelectedProjIds(initialSelected.projIds)
  }

  const handleConfirm = () => {
    onConfirm([...selectedExpIds], [...selectedProjIds])
  }

  const { job_analysis } = analysisResult

  const selectedExps = rankedExperiences.filter((e) => selectedExpIds.has(e.id))
  const availableExps = rankedExperiences.filter((e) => !selectedExpIds.has(e.id))
  const selectedProjs = rankedProjects.filter((p) => selectedProjIds.has(p.id))
  const availableProjs = rankedProjects.filter((p) => !selectedProjIds.has(p.id))

  const hasContent = rankedExperiences.length > 0 || rankedProjects.length > 0

  return (
    <div className="space-y-5">
      {/* Job context banner */}
      <div className="rounded-xl border border-slate-800/70 bg-white/5 px-4 py-3">
        <p className="text-sm font-semibold text-white">
          {selectedJob?.title ?? job_analysis.job_title}
          {(selectedJob?.company ?? job_analysis.company)
            ? ` @ ${selectedJob?.company ?? job_analysis.company}`
            : ''}
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {job_analysis.technologies.slice(0, 8).map((t) => (
            <span key={t} className="rounded-lg border border-indigo-500/30 bg-indigo-500/8 px-2 py-0.5 text-xs text-indigo-300">
              {t}
            </span>
          ))}
          {job_analysis.keywords.slice(0, 6).map((k) => (
            <span key={k} className="rounded-lg border border-slate-700 bg-white/5 px-2 py-0.5 text-xs text-slate-400">
              {k}
            </span>
          ))}
        </div>
      </div>

      {/* Selection counter + reset */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          <span className={`font-semibold ${atMax ? 'text-amber-400' : 'text-white'}`}>{totalSelected}</span>
          <span> / {MAX_SELECTIONS} items selected</span>
        </p>
        <button onClick={handleReset} className="text-xs text-slate-500 transition hover:text-slate-300">
          Reset to auto-selection
        </button>
      </div>

      {atMax && (
        <p className="text-xs text-amber-400/80">
          Maximum {MAX_SELECTIONS} items selected. Deselect an item to add another.
        </p>
      )}

      {/* Two-column layout */}
      {hasContent ? (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <SelectionColumn
            label="Work Experience"
            selectedItems={selectedExps}
            availableItems={availableExps}
            onToggle={toggleExp}
            atMax={atMax}
            renderTitle={(item) => ('title' in item ? item.title : '')}
            renderSubtitle={(item) =>
              'company' in item ? [item.company, item.location].filter(Boolean).join(' · ') : ''
            }
          />
          <SelectionColumn
            label="Projects"
            selectedItems={selectedProjs}
            availableItems={availableProjs}
            onToggle={toggleProj}
            atMax={atMax}
            renderTitle={(item) => ('name' in item ? item.name : '')}
            renderSubtitle={(item) => ('technologies' in item ? item.technologies : '')}
          />
        </div>
      ) : (
        <p className="text-sm italic text-slate-600">
          No experiences or projects in your resume yet. Add some in the sections above.
        </p>
      )}

      {/* Confirm button */}
      <button
        onClick={handleConfirm}
        disabled={totalSelected === 0 || optimizing}
        className={`w-full rounded-xl border px-4 py-3 text-sm font-semibold transition ${
          totalSelected === 0 || optimizing
            ? 'cursor-not-allowed border-slate-800 bg-white/5 text-slate-600'
            : 'border-indigo-500/70 bg-indigo-500/15 text-white shadow-[0_10px_40px_rgba(79,70,229,0.3)] hover:bg-indigo-500/25'
        }`}
      >
        {optimizing ? (
          <span className="flex items-center justify-center gap-2">
            <span className="h-4 w-4 animate-spin rounded-full border-b-2 border-indigo-400" />
            Optimizing with AI...
          </span>
        ) : (
          `Optimize ${totalSelected} Item${totalSelected !== 1 ? 's' : ''} with AI →`
        )}
      </button>
    </div>
  )
}

import { useEffect, useState, useCallback } from 'react'
import type { Resume, Experience, Project } from '../../types/Resume'
import type { Job } from '../../types/Job'
import { useResume } from '../../hooks/useResume'
import { PersonalInfoSection } from './sections/PersonalInfoSection'
import { EducationSection } from './sections/EducationSection'
import { SkillsSection } from './sections/SkillsSection'
import { ExperienceSection } from './sections/ExperienceSection'
import { ProjectSection } from './sections/ProjectSection'
import { ExperienceForm } from './forms/ExperienceForm'
import { ProjectForm } from './forms/ProjectForm'
import { JobOptimizer } from './optimization/JobOptimizer'

type SectionKey = 'personal' | 'education' | 'skills' | 'experience' | 'projects'

type Modal =
  | { type: 'addExperience' }
  | { type: 'editExperience'; id: string }
  | { type: 'addProject' }
  | { type: 'editProject'; id: string }
  | null

interface ResumeBuilderProps {
  /** Jobs from the dashboard — passed down so JobOptimizer can list them */
  jobs?: Job[]
  /** If set, immediately open the optimizer for this job ID */
  initialOptimizeJobId?: string
  /** Called once after initialOptimizeJobId has been consumed, so App can clear it */
  onOptimizeJobConsumed?: () => void
}

export function ResumeBuilder({ jobs = [], initialOptimizeJobId, onOptimizeJobConsumed }: ResumeBuilderProps) {
  const { resume, loading, saving, error, loadResume, saveResume, clearError } = useResume()

  const [localResume, setLocalResume] = useState<Resume | null>(null)
  const [isDirty, setIsDirty] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [modal, setModal] = useState<Modal>(null)

  const [expanded, setExpanded] = useState<Record<SectionKey, boolean>>({
    personal:   true,
    education:  false,
    skills:     false,
    experience: false,
    projects:   false,
  })

  // Load resume on mount
  useEffect(() => {
    loadResume()
  }, [loadResume])

  // Sync server data into local state
  useEffect(() => {
    if (resume) {
      setLocalResume(resume)
      setIsDirty(false)
    }
  }, [resume])

  const toggleSection = useCallback((key: SectionKey) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }))
  }, [])

  const updateResume = useCallback((patch: Partial<Resume>) => {
    setLocalResume((prev) => (prev ? { ...prev, ...patch } : prev))
    setIsDirty(true)
    setSaveSuccess(false)
  }, [])

  const handleSave = async () => {
    if (!localResume) return
    const ok = await saveResume(localResume)
    if (ok) {
      setIsDirty(false)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    }
  }

  const handleLoadSample = async () => {
    try {
      const response = await fetch('/api/resume/sample')
      if (response.ok) {
        const data: Resume = await response.json()
        setLocalResume(data)
        setIsDirty(true)
        setSaveSuccess(false)
      }
    } catch {
      // silently ignore — user can retry
    }
  }

  // ── Experience modal handlers ──────────────────────────────────────────────
  const handleExperienceSave = useCallback(
    (exp: Experience) => {
      if (!localResume) return
      const existing = localResume.experiences.find((e) => e.id === exp.id)
      const updated = existing
        ? localResume.experiences.map((e) => (e.id === exp.id ? exp : e))
        : [...localResume.experiences, exp]
      updateResume({ experiences: updated })
      setModal(null)
    },
    [localResume, updateResume]
  )

  // ── Project modal handlers ─────────────────────────────────────────────────
  const handleProjectSave = useCallback(
    (proj: Project) => {
      if (!localResume) return
      const existing = localResume.projects.find((p) => p.id === proj.id)
      const updated = existing
        ? localResume.projects.map((p) => (p.id === proj.id ? proj : p))
        : [...localResume.projects, proj]
      updateResume({ projects: updated })
      setModal(null)
    },
    [localResume, updateResume]
  )

  // ── Derived values for modal ───────────────────────────────────────────────
  const editingExperience =
    modal?.type === 'editExperience'
      ? localResume?.experiences.find((e) => e.id === modal.id)
      : undefined

  const editingProject =
    modal?.type === 'editProject'
      ? localResume?.projects.find((p) => p.id === modal.id)
      : undefined

  // ── Loading state ──────────────────────────────────────────────────────────
  if (loading && !localResume) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-b-2 border-indigo-500" />
          <p className="text-sm text-slate-400">Loading resume...</p>
        </div>
      </div>
    )
  }

  if (!localResume) return null

  return (
    <>
      <div className="space-y-4">
        {/* ── Page header ──────────────────────────────────────────────────── */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Builder</p>
            <h2 className="mt-1 text-2xl font-semibold text-white">Resume Builder</h2>
          </div>

          <div className="flex items-center gap-3">
            {/* Status indicators */}
            {error && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-red-400">{error}</span>
                <button onClick={clearError} className="text-xs text-slate-500 hover:text-slate-300">
                  ×
                </button>
              </div>
            )}
            {saveSuccess && (
              <span className="text-xs text-emerald-400">Saved successfully</span>
            )}
            {isDirty && !saveSuccess && (
              <span className="text-xs text-slate-500">Unsaved changes</span>
            )}

            <button
              onClick={handleLoadSample}
              className="rounded-xl border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
            >
              Load Sample
            </button>

            <button
              onClick={handleSave}
              disabled={saving || !isDirty}
              className={`rounded-xl border px-4 py-2 text-sm font-semibold transition ${
                saving || !isDirty
                  ? 'cursor-not-allowed border-slate-800 bg-white/5 text-slate-600'
                  : 'border-indigo-500/70 bg-indigo-500/15 text-white shadow-[0_10px_40px_rgba(79,70,229,0.3)] hover:bg-indigo-500/25'
              }`}
            >
              {saving ? 'Saving...' : 'Save Resume'}
            </button>
          </div>
        </div>

        {/* ── Collapsible sections ─────────────────────────────────────────── */}
        <PersonalInfoSection
          data={localResume.personal_info}
          expanded={expanded.personal}
          onToggle={() => toggleSection('personal')}
          onChange={(personal_info) => updateResume({ personal_info })}
        />

        <EducationSection
          data={localResume.education}
          expanded={expanded.education}
          onToggle={() => toggleSection('education')}
          onChange={(education) => updateResume({ education })}
        />

        <SkillsSection
          data={localResume.technical_skills}
          expanded={expanded.skills}
          onToggle={() => toggleSection('skills')}
          onChange={(technical_skills) => updateResume({ technical_skills })}
        />

        <ExperienceSection
          data={localResume.experiences}
          expanded={expanded.experience}
          onToggle={() => toggleSection('experience')}
          onChange={(experiences) => updateResume({ experiences })}
          onAdd={() => setModal({ type: 'addExperience' })}
          onEdit={(id) => setModal({ type: 'editExperience', id })}
        />

        <ProjectSection
          data={localResume.projects}
          expanded={expanded.projects}
          onToggle={() => toggleSection('projects')}
          onChange={(projects) => updateResume({ projects })}
          onAdd={() => setModal({ type: 'addProject' })}
          onEdit={(id) => setModal({ type: 'editProject', id })}
        />

        {/* ── Job Optimization Panel ───────────────────────────────────────── */}
        <JobOptimizer
          hasResume={Boolean(localResume)}
          resume={localResume}
          jobs={jobs}
          initialJobId={initialOptimizeJobId}
          onInitialJobConsumed={onOptimizeJobConsumed}
        />
      </div>

      {/* ── Modals ───────────────────────────────────────────────────────────── */}
      {(modal?.type === 'addExperience' || modal?.type === 'editExperience') && (
        <ExperienceForm
          experience={editingExperience}
          onSave={handleExperienceSave}
          onCancel={() => setModal(null)}
        />
      )}

      {(modal?.type === 'addProject' || modal?.type === 'editProject') && (
        <ProjectForm
          project={editingProject}
          onSave={handleProjectSave}
          onCancel={() => setModal(null)}
        />
      )}
    </>
  )
}

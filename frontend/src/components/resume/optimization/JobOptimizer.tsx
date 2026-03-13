import { useState } from 'react'
import { useOptimization } from '../../../hooks/useOptimization'
import type { Job } from '../../../types/Job'
import type { JobAnalysisResult, OptimizedContent, Resume } from '../../../types/Resume'
import { ContentSelector } from './ContentSelector'
import { OptimizationReview } from './OptimizationReview'
import { PDFPreview } from './PDFPreview'

type OptimizationStep = 'select-job' | 'select-content' | 'review' | 'pdf'

interface JobOptimizerProps {
  hasResume: boolean
  resume: Resume | null
  jobs: Job[]
}

export function JobOptimizer({ hasResume, resume, jobs }: JobOptimizerProps) {
  const [step, setStep] = useState<OptimizationStep>('select-job')
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null)
  const [analysisResult, setAnalysisResult] = useState<JobAnalysisResult | null>(null)
  const [optimizedContent, setOptimizedContent] = useState<OptimizedContent | null>(null)
  const [selectedExperiences, setSelectedExperiences] = useState<string[]>([])
  const [selectedProjects, setSelectedProjects] = useState<string[]>([])

  const { analyzeJob, optimizeResume, analyzing, optimizing, error, clearError } = useOptimization()

  if (!hasResume || !resume) return null

  const selectedJob = jobs.find((j) => j.id === selectedJobId)

  const handleJobSelect = async (jobId: string) => {
    setSelectedJobId(jobId)
    clearError()
    const result = await analyzeJob(jobId)
    if (result) {
      setAnalysisResult(result)
      setStep('select-content')
    }
  }

  const handleContentConfirmed = async (expIds: string[], projIds: string[]) => {
    if (!selectedJobId) return
    setSelectedExperiences(expIds)
    setSelectedProjects(projIds)
    clearError()
    const content = await optimizeResume(selectedJobId, expIds, projIds)
    if (content) {
      setOptimizedContent(content)
      setStep('review')
    }
  }

  const handleReviewDone = (finalContent: OptimizedContent) => {
    setOptimizedContent(finalContent)
    setStep('pdf')
  }

  const handleReset = () => {
    setStep('select-job')
    setSelectedJobId(null)
    setAnalysisResult(null)
    setOptimizedContent(null)
    setSelectedExperiences([])
    setSelectedProjects([])
    clearError()
  }

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
      {/* Section header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/70">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">AI Optimization</p>
          <p className="mt-0.5 text-base font-semibold text-white">Job Optimizer</p>
        </div>
        {step !== 'select-job' && (
          <button
            onClick={handleReset}
            className="text-xs text-slate-500 transition hover:text-slate-300"
          >
            ← Start over
          </button>
        )}
      </div>

      <div className="px-6 py-5">
        {/* Step breadcrumb */}
        {step !== 'select-job' && (
          <div className="mb-5 flex items-center gap-2 text-xs text-slate-500">
            {(['select-content', 'review', 'pdf'] as const).map((s, i) => {
              const labels = { 'select-content': 'Select Content', review: 'Review', pdf: 'Download PDF' }
              const stepOrder = { 'select-content': 0, review: 1, pdf: 2 }
              const currentOrder = stepOrder[step as keyof typeof stepOrder] ?? -1
              const thisOrder = stepOrder[s]
              const isDone = currentOrder > thisOrder
              const isActive = step === s
              return (
                <span key={s} className="flex items-center gap-2">
                  {i > 0 && <span>›</span>}
                  <span className={isActive ? 'text-indigo-400 font-medium' : isDone ? 'text-emerald-500' : ''}>
                    {isDone ? '✓ ' : ''}{labels[s]}
                  </span>
                </span>
              )
            })}
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="mb-4 flex items-center justify-between rounded-xl border border-red-900/40 bg-red-900/10 px-4 py-3">
            <p className="text-sm text-red-400">{error}</p>
            <button onClick={clearError} className="text-xs text-slate-500 hover:text-slate-300">×</button>
          </div>
        )}

        {/* Step 1 — Job selection */}
        {step === 'select-job' && (
          <div className="space-y-3">
            <p className="text-sm text-slate-400">
              Select a job from your dashboard to analyze, score, and AI-optimize your resume bullet points for that specific role.
            </p>

            {jobs.length === 0 ? (
              <p className="text-sm italic text-slate-600">No jobs in your dashboard yet.</p>
            ) : (
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {jobs.map((job) => (
                  <button
                    key={job.id}
                    onClick={() => handleJobSelect(job.id)}
                    disabled={analyzing}
                    className="w-full rounded-xl border border-slate-800/70 bg-white/5 px-4 py-3 text-left transition hover:border-indigo-500/40 hover:bg-indigo-500/5 disabled:opacity-50"
                  >
                    <p className="text-sm font-semibold text-white">{job.title}</p>
                    <p className="text-xs text-slate-400">
                      {job.company}
                      {job.company && job.location ? ' · ' : ''}
                      {job.location}
                    </p>
                  </button>
                ))}
              </div>
            )}

            {analyzing && (
              <div className="flex items-center gap-3 rounded-xl border border-slate-800/70 bg-white/5 px-4 py-3">
                <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-indigo-400 shrink-0" />
                <p className="text-sm text-slate-400">Analyzing job requirements and scoring your resume...</p>
              </div>
            )}
          </div>
        )}

        {/* Step 2 — Content selection */}
        {step === 'select-content' && analysisResult && resume && (
          <ContentSelector
            analysisResult={analysisResult}
            resume={resume}
            selectedJob={selectedJob ?? null}
            onConfirm={handleContentConfirmed}
            optimizing={optimizing}
          />
        )}

        {/* Step 3 — Review */}
        {step === 'review' && optimizedContent && resume && analysisResult && (
          <OptimizationReview
            resume={resume}
            optimizedContent={optimizedContent}
            analysisResult={analysisResult}
            selectedExperienceIds={selectedExperiences}
            selectedProjectIds={selectedProjects}
            selectedJob={selectedJob ?? null}
            onDone={handleReviewDone}
            onBack={() => setStep('select-content')}
          />
        )}

        {/* Step 4 — PDF */}
        {step === 'pdf' && optimizedContent && selectedJob && (
          <PDFPreview
            jobId={selectedJob.id}
            jobTitle={selectedJob.title ?? ''}
            company={selectedJob.company ?? ''}
            optimizedContent={optimizedContent}
            selectedExperienceIds={selectedExperiences}
            selectedProjectIds={selectedProjects}
            onBack={() => setStep('review')}
            onStartOver={handleReset}
          />
        )}
      </div>
    </div>
  )
}

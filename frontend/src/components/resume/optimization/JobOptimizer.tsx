// Phase 3+ — Job optimization flow entry point.
// Receives the master resume and lets the user pick a job to optimize against.

interface JobOptimizerProps {
  hasResume: boolean
}

export function JobOptimizer({ hasResume }: JobOptimizerProps) {
  if (!hasResume) return null

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-white/5 p-6 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">AI Optimization</p>
          <p className="mt-0.5 text-base font-semibold text-white">Job Optimizer</p>
        </div>
        <span className="rounded-full border border-slate-700 bg-white/5 px-3 py-1 text-xs text-slate-400">
          Coming in Phase 3
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-400">
        Select a job from your dashboard to analyze, score, and AI-optimize your resume bullet points for that specific role.
      </p>
    </div>
  )
}

import { useState } from 'react'
import type { OptimizedContent } from '../../../types/Resume'

interface PDFPreviewProps {
  jobId: string
  jobTitle: string
  company: string
  optimizedContent: OptimizedContent
  selectedExperienceIds: string[]
  selectedProjectIds: string[]
  onBack: () => void
  onStartOver: () => void
}

type PdfStatus = 'idle' | 'generating' | 'ready' | 'error'

export function PDFPreview({
  jobId,
  jobTitle,
  company,
  optimizedContent,
  onBack,
  onStartOver,
}: PDFPreviewProps) {
  const [status, setStatus] = useState<PdfStatus>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const totalBullets = [
    ...Object.values(optimizedContent.experiences).flatMap((e) => e.optimized_bullet_points),
    ...Object.values(optimizedContent.projects).flatMap((p) => p.optimized_bullet_points),
  ].length

  const expCount = Object.keys(optimizedContent.experiences).length
  const projCount = Object.keys(optimizedContent.projects).length

  const handleGeneratePDF = async () => {
    setStatus('generating')
    setErrorMessage(null)
    try {
      const response = await fetch(`/api/resume/generate-pdf/${jobId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(optimizedContent),
      })

      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail ?? `PDF generation failed: ${response.status}`)
      }

      setStatus('ready')
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : 'PDF generation failed')
      setStatus('error')
    }
  }

  const handleDownload = () => {
    // Opens the download endpoint in a new tab — browser handles the PDF download
    window.open(`/api/resume/download/${jobId}`, '_blank')
  }

  return (
    <div className="space-y-5">
      {/* Summary card */}
      <div className="rounded-xl border border-slate-800/70 bg-white/5 px-4 py-4">
        <p className="text-sm font-semibold text-white">
          Resume ready for{' '}
          <span className="text-indigo-300">{jobTitle || 'Unknown Role'}</span>
          {company ? ` @ ${company}` : ''}
        </p>
        <div className="mt-3 flex flex-wrap gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
            {expCount} experience{expCount !== 1 ? 's' : ''}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-purple-400" />
            {projCount} project{projCount !== 1 ? 's' : ''}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
            {totalBullets} optimized bullet{totalBullets !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Status / actions */}
      {status === 'idle' && (
        <div className="space-y-3">
          <p className="text-sm text-slate-400">
            Your resume is optimized and ready. Generate the PDF using the LaTeX template.
          </p>
          <button
            onClick={handleGeneratePDF}
            className="w-full rounded-xl border border-indigo-500/70 bg-indigo-500/15 px-4 py-3 text-sm font-semibold text-white shadow-[0_10px_40px_rgba(79,70,229,0.3)] transition hover:bg-indigo-500/25"
          >
            Generate PDF
          </button>
        </div>
      )}

      {status === 'generating' && (
        <div className="flex items-center gap-3 rounded-xl border border-slate-800/70 bg-white/5 px-4 py-4">
          <div className="h-5 w-5 animate-spin rounded-full border-b-2 border-indigo-400 shrink-0" />
          <div>
            <p className="text-sm font-medium text-white">Compiling PDF...</p>
            <p className="text-xs text-slate-500">Rendering LaTeX template and compiling with pdflatex</p>
          </div>
        </div>
      )}

      {status === 'ready' && (
        <div className="space-y-3">
          <div className="flex items-center gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/8 px-4 py-3">
            <span className="text-emerald-400 text-lg">✓</span>
            <p className="text-sm font-medium text-emerald-300">PDF generated successfully!</p>
          </div>
          <button
            onClick={handleDownload}
            className="w-full rounded-xl border border-emerald-500/50 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-500/20"
          >
            ↓ Download PDF
          </button>
          <button
            onClick={handleGeneratePDF}
            className="w-full rounded-xl border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-400 transition hover:text-white"
          >
            Regenerate
          </button>
        </div>
      )}

      {status === 'error' && (
        <div className="space-y-3">
          <div className="rounded-xl border border-red-900/40 bg-red-900/10 px-4 py-3">
            <p className="text-sm font-medium text-red-400">PDF generation failed</p>
            {errorMessage && <p className="mt-1 text-xs text-red-400/70">{errorMessage}</p>}
          </div>
          <button
            onClick={handleGeneratePDF}
            className="w-full rounded-xl border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:text-white"
          >
            Try again
          </button>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-800/70">
        <button
          onClick={onBack}
          className="rounded-xl border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
        >
          ← Back to Review
        </button>
        <button
          onClick={onStartOver}
          className="text-xs text-slate-500 transition hover:text-slate-300"
        >
          Optimize another job
        </button>
      </div>
    </div>
  )
}

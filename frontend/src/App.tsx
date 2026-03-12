import { useEffect, useMemo, useState } from 'react'
import { useJobs } from './hooks/useJobs'
import { formatDate } from './utils/formatDate'
import { JobDescription } from './components/JobDescription'
import { ResumeBuilder } from './components/resume/ResumeBuilder'

type Tab = 'ready' | 'applied' | 'all'
type View = 'jobs' | 'resume'

function App() {
  const [currentView, setCurrentView] = useState<View>('jobs')
  const [activeTab, setActiveTab] = useState<Tab>('all')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const { jobs, loading, error } = useJobs()

  const counts = useMemo(() => ({
    ready: jobs.filter((job) => job.status === 'ready').length,
    applied: jobs.filter((job) => job.status === 'applied').length,
    all: jobs.length,
  }), [jobs])

  const filteredJobs = useMemo(() => {
    if (activeTab === 'all') return jobs
    return jobs.filter((job) => job.status === activeTab)
  }, [activeTab, jobs])

  useEffect(() => {
    if (!filteredJobs.length) {
      setSelectedId(null)
      return
    }

    const alreadySelected = filteredJobs.some((job) => job.id === selectedId)
    if (!alreadySelected) {
      setSelectedId(filteredJobs[0].id)
    }
  }, [filteredJobs, selectedId])

  const selectedJob = filteredJobs.find((job) => job.id === selectedId) ?? filteredJobs[0]

  if (loading) {
    return (
      <div className="min-h-screen bg-linear-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading jobs...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-linear-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">Error loading jobs</p>
          <p className="text-slate-500 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { key: 'ready', label: 'Ready', count: counts.ready },
    { key: 'applied', label: 'Applied', count: counts.applied },
    { key: 'all', label: 'All Jobs', count: counts.all },
  ]

  return (
    <div className="min-h-screen bg-linear-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-10 lg:px-10 lg:py-12">
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Dashboard</p>
              <h1 className="mt-2 text-3xl font-semibold text-white">PlsFindMeAJob</h1>
            </div>

            <nav className="flex gap-2">
              <button
                onClick={() => setCurrentView('jobs')}
                className={`rounded-xl border px-4 py-2 text-sm font-medium transition ${
                  currentView === 'jobs'
                    ? 'border-indigo-500/70 bg-indigo-500/15 text-white shadow-[0_10px_40px_rgba(79,70,229,0.3)]'
                    : 'border-slate-800 bg-white/5 text-slate-400 hover:border-slate-600 hover:text-white'
                }`}
              >
                Job Dashboard
              </button>
              <button
                onClick={() => setCurrentView('resume')}
                className={`rounded-xl border px-4 py-2 text-sm font-medium transition ${
                  currentView === 'resume'
                    ? 'border-indigo-500/70 bg-indigo-500/15 text-white shadow-[0_10px_40px_rgba(79,70,229,0.3)]'
                    : 'border-slate-800 bg-white/5 text-slate-400 hover:border-slate-600 hover:text-white'
                }`}
              >
                Resume Builder
              </button>
            </nav>
          </div>

          <div className="rounded-full border border-slate-800 bg-white/5 px-4 py-2 text-sm text-slate-300 shadow-sm shadow-indigo-950/40">
            {counts.all} total roles
          </div>
        </div>

        {currentView === 'resume' ? (
          <ResumeBuilder />
        ) : (
          <>
        <div className="mb-6 flex gap-3 overflow-x-auto pb-2">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.key
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as Tab)}
                className={`flex items-center gap-2 rounded-xl border px-4 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'border-indigo-500/70 bg-indigo-500/15 text-white shadow-[0_10px_40px_rgba(79,70,229,0.3)]'
                    : 'border-slate-800 bg-white/5 text-slate-300 hover:border-slate-600'
                }`}
              >
                <span>{tab.label}</span>
                <span
                  className={`rounded-lg px-2 py-1 text-xs font-semibold ${
                    isActive ? 'bg-white/15 text-white' : 'bg-slate-800 text-slate-300'
                  }`}
                >
                  {tab.count}
                </span>
              </button>
            )
          })}
        </div>

        <div className="grid gap-6 lg:grid-cols-12">
          <section className="lg:col-span-5">
            <div className="overflow-hidden rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
              <div className="border-b border-slate-800/70 bg-white/5 px-5 py-4">
                <p className="text-sm text-slate-400">Job list</p>
                <p className="text-base font-semibold text-white">{filteredJobs.length} matches</p>
              </div>
              <div className="divide-y divide-slate-800/70">
                {filteredJobs.map((job) => {
                  const isSelected = job.id === selectedJob?.id
                  return (
                    <button
                      key={job.id}
                      onClick={() => setSelectedId(job.id)}
                      className={`flex w-full flex-col items-start gap-2 px-5 py-4 text-left transition ${
                        isSelected
                          ? 'bg-indigo-500/10 shadow-inner shadow-indigo-900/60'
                          : 'hover:bg-white/10'
                      }`}
                    >
                      <div className="flex w-full items-center justify-between gap-3">
                        <div className="flex flex-col">
                          <p className="text-sm uppercase tracking-[0.2em] text-slate-500">{job.site}</p>
                          <p className="mt-1 text-sm text-slate-400">{job.company}</p>
                        </div>
                        <span className="rounded-full border border-slate-700 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200">
                          {job.is_remote ? 'Remote' : (job.location || 'Location TBD')}
                        </span>
                      </div>
                      <p className="text-base font-semibold text-white">{job.title}</p>
                      <div className="flex w-full items-center justify-between text-xs text-slate-500">
                        <span>{job.experience_range || 'N/A'}</span>
                        <span>{formatDate(job.date_posted || '')}</span>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </section>

          <section className="lg:col-span-7">
            <div className="flex h-full flex-col gap-4 rounded-2xl border border-slate-800/80 bg-white/5 p-6 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
              {selectedJob ? (
                <>
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="text-sm uppercase tracking-[0.25em] text-slate-500">{selectedJob.site}</p>
                      <h2 className="mt-2 text-2xl font-semibold text-white">{selectedJob.title}</h2>
                      <p className="text-sm text-slate-400">{selectedJob.company}</p>
                    </div>
                    <button className="flex items-center gap-2 rounded-full bg-linear-to-r from-indigo-500 via-purple-500 to-fuchsia-500 px-5 py-2 text-sm font-semibold text-white shadow-[0_15px_45px_-10px_rgba(79,70,229,0.5)] transition hover:shadow-[0_20px_55px_-12px_rgba(79,70,229,0.65)]">
                      Generate Resume
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-3 text-sm text-slate-300">
                    {selectedJob.location && (
                      <span className="rounded-lg border border-slate-700 bg-white/5 px-3 py-1">{selectedJob.location}</span>
                    )}
                    {selectedJob.job_type && (
                      <span className="rounded-lg border border-slate-700 bg-white/5 px-3 py-1">{selectedJob.job_type}</span>
                    )}
                    {selectedJob.skills && (
                      <span className="rounded-lg border border-slate-700 bg-white/5 px-3 py-1">{selectedJob.skills}</span>
                    )}
                    {selectedJob.is_remote && (
                      <span className="rounded-lg border border-slate-700 bg-white/5 px-3 py-1">Remote</span>
                    )}
                  </div>

                  <div className="rounded-xl border border-slate-800/70 bg-[#0c1325]/80 p-4 text-sm leading-relaxed text-slate-200 shadow-inner shadow-indigo-950/30">
                    <JobDescription content={selectedJob.description || 'No description available'} />
                  </div>

                  <div className="flex flex-wrap gap-4 text-sm text-slate-400">
                    {(selectedJob.job_url_direct || selectedJob.job_url) && (
                      <a
                        href={selectedJob.job_url_direct || selectedJob.job_url || '#'}
                        className="rounded-full border border-slate-700 bg-white/5 px-4 py-2 font-semibold text-indigo-200 transition hover:border-indigo-500/70 hover:text-white"
                        target="_blank"
                        rel="noreferrer"
                      >
                        View posting
                      </a>
                    )}
                    {(selectedJob.company_url_direct || selectedJob.company_url) && (
                      <a
                        href={selectedJob.company_url_direct || selectedJob.company_url || '#'}
                        className="rounded-full border border-slate-700 bg-white/5 px-4 py-2 font-semibold text-slate-200 transition hover:border-indigo-500/70 hover:text-white"
                        target="_blank"
                        rel="noreferrer"
                      >
                        Company site
                      </a>
                    )}
                  </div>
                </>
              ) : (
                <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-slate-800/80 bg-white/10 text-slate-400">
                  No jobs available in this tab.
                </div>
              )}
            </div>
          </section>
        </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App
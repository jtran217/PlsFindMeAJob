import { useEffect, useState } from 'react'
import { useScraper } from '../../hooks/useScraper'
import type { JobSite, ScraperSettings as ScraperSettingsType } from '../../types/Scraper'

const SITE_LABELS: Record<JobSite, string> = {
  indeed: 'Indeed',
  linkedin: 'LinkedIn',
  glassdoor: 'Glassdoor',
  zip_recruiter: 'ZipRecruiter',
}

const ALL_SITES: JobSite[] = ['indeed', 'linkedin', 'glassdoor', 'zip_recruiter']

const INTERVAL_OPTIONS: { label: string; value: number }[] = [
  { label: 'Every 1 hour', value: 1 },
  { label: 'Every 6 hours', value: 6 },
  { label: 'Every 12 hours', value: 12 },
  { label: 'Every 24 hours', value: 24 },
  { label: 'Every 48 hours', value: 48 },
  { label: 'Every 7 days', value: 168 },
]

function formatTimestamp(iso: string | null): string {
  if (!iso) return 'Never'
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function ScraperSettings({ onScrapeComplete }: { onScrapeComplete?: () => void }) {
  const { settings, status, saving, running, error, saveSettings, runNow } = useScraper(onScrapeComplete)
  const [local, setLocal] = useState<ScraperSettingsType | null>(null)
  const [saveSuccess, setSaveSuccess] = useState(false)

  // Sync server settings into local form state
  useEffect(() => {
    if (settings) setLocal(settings)
  }, [settings])

  const handleSave = async () => {
    if (!local) return
    setSaveSuccess(false)
    await saveSettings(local)
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
  }

  const toggleSite = (site: JobSite) => {
    if (!local) return
    const current = local.sites
    const next = current.includes(site)
      ? current.filter((s) => s !== site)
      : [...current, site]
    // Prevent deselecting all sites
    if (next.length === 0) return
    setLocal({ ...local, sites: next })
  }

  if (!local) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-500"></div>
      </div>
    )
  }

  const inputClass =
    'w-full rounded-xl border border-slate-700 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-slate-500 outline-none focus:border-indigo-500/70 focus:ring-1 focus:ring-indigo-500/40 transition'

  const labelClass = 'block text-xs uppercase tracking-widest text-slate-500 mb-1.5'

  return (
    <div className="mx-auto max-w-2xl">
      <div className="overflow-hidden rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
        {/* Header */}
        <div className="border-b border-slate-800/70 bg-white/5 px-6 py-5">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Configuration</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Job Scraper Settings</h2>
        </div>

        <div className="px-6 py-6 space-y-6">
          {/* Error banner */}
          {error && (
            <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {/* Search term + Location */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className={labelClass}>Search Term</label>
              <input
                type="text"
                className={inputClass}
                value={local.search_term}
                onChange={(e) => setLocal({ ...local, search_term: e.target.value })}
                placeholder="e.g. software engineer"
              />
            </div>
            <div>
              <label className={labelClass}>Location</label>
              <input
                type="text"
                className={inputClass}
                value={local.location}
                onChange={(e) => setLocal({ ...local, location: e.target.value })}
                placeholder="e.g. Calgary"
              />
            </div>
          </div>

          {/* Schedule + Enabled */}
          <div className="grid gap-4 sm:grid-cols-2 items-end">
            <div>
              <label className={labelClass}>Schedule</label>
              <select
                className={inputClass}
                value={local.interval_hours}
                onChange={(e) => setLocal({ ...local, interval_hours: Number(e.target.value) })}
              >
                {INTERVAL_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value} className="bg-[#0b1228]">
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-slate-700 bg-white/5 px-4 py-3">
              <span className="text-sm text-slate-300">Scheduler enabled</span>
              <button
                type="button"
                onClick={() => setLocal({ ...local, enabled: !local.enabled })}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none ${
                  local.enabled ? 'bg-indigo-500' : 'bg-slate-700'
                }`}
                role="switch"
                aria-checked={local.enabled}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition duration-200 ${
                    local.enabled ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Results per run + Job age filter */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className={labelClass}>Results per run</label>
              <input
                type="number"
                min={1}
                max={100}
                className={inputClass}
                value={local.results_wanted}
                onChange={(e) => setLocal({ ...local, results_wanted: Number(e.target.value) })}
              />
            </div>
            <div>
              <label className={labelClass}>Job age filter (hours)</label>
              <input
                type="number"
                min={1}
                max={720}
                className={inputClass}
                value={local.hours_old}
                onChange={(e) => setLocal({ ...local, hours_old: Number(e.target.value) })}
              />
            </div>
          </div>

          {/* Job Sites */}
          <div>
            <label className={labelClass}>Job Sites</label>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {ALL_SITES.map((site) => {
                const checked = local.sites.includes(site)
                return (
                  <button
                    key={site}
                    type="button"
                    onClick={() => toggleSite(site)}
                    className={`flex items-center gap-2 rounded-xl border px-3 py-2.5 text-sm font-medium transition ${
                      checked
                        ? 'border-indigo-500/70 bg-indigo-500/15 text-white'
                        : 'border-slate-700 bg-white/5 text-slate-400 hover:border-slate-600 hover:text-white'
                    }`}
                  >
                    <span
                      className={`h-4 w-4 shrink-0 rounded border flex items-center justify-center transition ${
                        checked ? 'border-indigo-400 bg-indigo-500' : 'border-slate-600 bg-transparent'
                      }`}
                    >
                      {checked && (
                        <svg className="h-2.5 w-2.5 text-white" viewBox="0 0 10 10" fill="none">
                          <path d="M1.5 5L4 7.5L8.5 2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      )}
                    </span>
                    {SITE_LABELS[site]}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Status Panel */}
          <div className="rounded-xl border border-slate-800/70 bg-[#0c1325]/80 p-4 shadow-inner shadow-indigo-950/30">
            <p className="text-xs uppercase tracking-widest text-slate-500 mb-3">Last Run</p>
            {status ? (
              <div className="space-y-1.5 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Ran at</span>
                  <span className="text-slate-200">{formatTimestamp(status.last_run)}</span>
                </div>
                {status.last_run && (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Jobs found</span>
                      <span className="text-slate-200">{status.last_run_jobs_found}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Jobs added</span>
                      <span className="text-slate-200">{status.last_run_jobs_added}</span>
                    </div>
                  </>
                )}
                <div className="flex items-center justify-between pt-1 border-t border-slate-800/70">
                  <span className="text-slate-400">Next run</span>
                  <span className="text-slate-200">{formatTimestamp(status.next_run)}</span>
                </div>
                {running && (
                  <div className="flex items-center gap-2 pt-1 text-indigo-300">
                    <div className="animate-spin h-3 w-3 rounded-full border-b border-indigo-400"></div>
                    <span className="text-xs">Scrape in progress...</span>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No status available.</p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between gap-4 pt-1">
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 rounded-xl border border-indigo-500/50 bg-indigo-500/15 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? (
                <>
                  <div className="animate-spin h-3.5 w-3.5 rounded-full border-b border-white"></div>
                  Saving...
                </>
              ) : saveSuccess ? (
                'Saved!'
              ) : (
                'Save Settings'
              )}
            </button>

            <button
              type="button"
              onClick={runNow}
              disabled={running}
              className="flex items-center gap-2 rounded-full bg-linear-to-r from-indigo-500 via-purple-500 to-fuchsia-500 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_15px_45px_-10px_rgba(79,70,229,0.5)] transition hover:shadow-[0_20px_55px_-12px_rgba(79,70,229,0.65)] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {running ? (
                <>
                  <div className="animate-spin h-3.5 w-3.5 rounded-full border-b border-white"></div>
                  Running...
                </>
              ) : (
                <>
                  <svg className="h-3.5 w-3.5" viewBox="0 0 12 12" fill="currentColor">
                    <path d="M2 2.5L10 6L2 9.5V2.5Z" />
                  </svg>
                  Run Now
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

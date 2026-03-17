import { useCallback, useEffect, useRef, useState } from 'react'
import type { ScraperSettings, ScraperStatus } from '../types/Scraper'

const API_BASE = '/api/scraper'
const POLL_INTERVAL_MS = 2000

export const useScraper = (onScrapeComplete?: () => void) => {
  const [settings, setSettings] = useState<ScraperSettings | null>(null)
  const [status, setStatus] = useState<ScraperStatus | null>(null)
  const [saving, setSaving] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pollTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const stopPolling = useCallback(() => {
    if (pollTimerRef.current !== null) {
      clearTimeout(pollTimerRef.current)
      pollTimerRef.current = null
    }
  }, [])

  const pollStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/status`)
      if (!res.ok) throw new Error(`Status fetch failed: ${res.status}`)
      const data: ScraperStatus = await res.json()
      setStatus(data)
      setRunning(data.is_running)

      if (data.is_running) {
        pollTimerRef.current = setTimeout(pollStatus, POLL_INTERVAL_MS)
      } else {
        stopPolling()
        onScrapeComplete?.()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch status')
      stopPolling()
    }
  }, [stopPolling, onScrapeComplete])

  const loadSettings = useCallback(async () => {
    try {
      setError(null)
      const [settingsRes, statusRes] = await Promise.all([
        fetch(`${API_BASE}/settings`),
        fetch(`${API_BASE}/status`),
      ])
      if (!settingsRes.ok) throw new Error(`Failed to load settings: ${settingsRes.status}`)
      if (!statusRes.ok) throw new Error(`Failed to load status: ${statusRes.status}`)

      const [settingsData, statusData] = await Promise.all([
        settingsRes.json() as Promise<ScraperSettings>,
        statusRes.json() as Promise<ScraperStatus>,
      ])

      setSettings(settingsData)
      setStatus(statusData)
      setRunning(statusData.is_running)

      if (statusData.is_running) {
        pollTimerRef.current = setTimeout(pollStatus, POLL_INTERVAL_MS)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scraper data')
    }
  }, [pollStatus])

  const saveSettings = useCallback(async (newSettings: ScraperSettings) => {
    setSaving(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings),
      })
      if (!res.ok) throw new Error(`Failed to save settings: ${res.status}`)
      const saved: ScraperSettings = await res.json()
      setSettings(saved)
      // Refresh status so next_run reflects the new schedule
      await pollStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }, [pollStatus])

  const runNow = useCallback(async () => {
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/run`, { method: 'POST' })
      if (res.status === 409) return // already running — button was disabled but guard anyway
      if (!res.ok) throw new Error(`Failed to trigger scrape: ${res.status}`)
      setRunning(true)
      // Start polling to track progress
      pollTimerRef.current = setTimeout(pollStatus, POLL_INTERVAL_MS)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start scrape')
    }
  }, [pollStatus])

  // Load on mount
  useEffect(() => {
    loadSettings()
    return () => stopPolling()
  }, [loadSettings, stopPolling])

  return {
    settings,
    status,
    saving,
    running,
    error,
    loadSettings,
    saveSettings,
    runNow,
    pollStatus,
  }
}

import { create } from 'zustand'

// ── Types ─────────────────────────────────────────────────────────────────────

export type JobStatus = 'queued' | 'uploading' | 'processing' | 'completed' | 'failed'

export interface ProcessingJob {
  id:          string     // unique UI id (not the server job_id)
  job_id:      string | null
  file_name:   string
  action:      string
  status:      JobStatus
  progress:    number     // 0-100
  error?:      string
  download?:   { blob: Blob; filename: string }
  created_at:  number     // Date.now()
}

interface ProcessingState {
  jobs:        ProcessingJob[]
  panelOpen:   boolean
  addJob:      (job: Omit<ProcessingJob, 'created_at'>) => void
  updateJob:   (id: string, patch: Partial<ProcessingJob>)  => void
  removeJob:   (id: string) => void
  clearDone:   () => void
  togglePanel: () => void
  openPanel:   () => void
}

// ── Store ─────────────────────────────────────────────────────────────────────

export const useProcessingStore = create<ProcessingState>((set) => ({
  jobs:      [],
  panelOpen: false,

  addJob: (job) =>
    set(s => ({
      jobs:      [...s.jobs, { ...job, created_at: Date.now() }],
      panelOpen: true,   // auto-open panel when a job is added
    })),

  updateJob: (id, patch) =>
    set(s => ({
      jobs: s.jobs.map(j => j.id === id ? { ...j, ...patch } : j),
    })),

  removeJob: (id) =>
    set(s => ({ jobs: s.jobs.filter(j => j.id !== id) })),

  clearDone: () =>
    set(s => ({
      jobs: s.jobs.filter(j => j.status !== 'completed' && j.status !== 'failed'),
    })),

  togglePanel: () => set(s => ({ panelOpen: !s.panelOpen })),
  openPanel:   () => set({ panelOpen: true }),
}))

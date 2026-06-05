import { useEffect } from 'react'
import { X, ChevronDown, ChevronUp, Loader2, CheckCircle2, AlertCircle, Clock } from 'lucide-react'
import { useProcessingStore, type ProcessingJob } from '@/store/processingStore'

const STATUS_META: Record<ProcessingJob['status'], {
  label: string
  icon:  React.ReactNode
  cls:   string
  bar:   string
}> = {
  queued:     { label: 'Queued',     icon: <Clock        size={13}/>,                                   cls: 'text-muted',       bar: 'bg-border'       },
  uploading:  { label: 'Uploading',  icon: <Loader2      size={13} className="animate-spin"/>,          cls: 'text-amber-600',   bar: 'bg-amber-400'    },
  processing: { label: 'Processing', icon: <Loader2      size={13} className="animate-spin"/>,          cls: 'text-primary',     bar: 'bg-primary'      },
  completed:  { label: 'Complete',   icon: <CheckCircle2 size={13}/>,                                   cls: 'text-emerald-600', bar: 'bg-emerald-500'  },
  failed:     { label: 'Failed',     icon: <AlertCircle  size={13}/>,                                   cls: 'text-red-500',     bar: 'bg-red-500'      },
}

function JobRow({ job }: { job: ProcessingJob }) {
  const { removeJob } = useProcessingStore()
  const meta          = STATUS_META[job.status]

  // Auto-dismiss completed jobs after 4 seconds
  useEffect(() => {
    if (job.status !== 'completed') return
    const t = setTimeout(() => removeJob(job.id), 4_000)
    return () => clearTimeout(t)
  }, [job.status, job.id, removeJob])

  return (
    <div className="px-3 py-2.5 border-b border-border last:border-0">
      <div className="flex items-start gap-2">
        <span className={`mt-0.5 flex-shrink-0 ${meta.cls}`}>{meta.icon}</span>

        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-text truncate">{job.action}</p>
          <p className="text-[10px] text-muted truncate">{job.file_name}</p>

          {/* Progress bar */}
          {(job.status === 'uploading' || job.status === 'processing') && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <div className="flex-1 h-1 bg-border rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${meta.bar}`}
                  style={{ width: `${job.progress}%` }}
                />
              </div>
              <span className="text-[10px] text-muted tabular-nums w-7 text-right">
                {job.progress}%
              </span>
            </div>
          )}

          {/* Completed message */}
          {job.status === 'completed' && (
            <p className="text-[10px] text-emerald-600 mt-0.5">
              Files saved successfully
            </p>
          )}

          {/* Error message */}
          {job.status === 'failed' && job.error && (
            <p className="text-[10px] text-red-500 mt-0.5 line-clamp-2">{job.error}</p>
          )}
        </div>

        {/* Dismiss button — only for failed (completed auto-dismisses) */}
        {job.status === 'failed' && (
          <button
            onClick={() => removeJob(job.id)}
            className="p-1 rounded text-muted hover:text-text hover:bg-surface transition-colors flex-shrink-0"
          >
            <X size={12}/>
          </button>
        )}
      </div>
    </div>
  )
}

export function ProcessingQueue() {
  const { jobs, panelOpen, togglePanel, clearDone } = useProcessingStore()

  if (jobs.length === 0) return null

  const active = jobs.filter(j =>
    j.status === 'queued' || j.status === 'uploading' || j.status === 'processing'
  ).length
  const done = jobs.filter(j => j.status === 'completed' || j.status === 'failed').length

  return (
    <div className="fixed bottom-4 right-4 z-50 w-72 bg-card border border-border rounded-xl shadow-2xl overflow-hidden">

      {/* Header */}
      <div
        className="flex items-center justify-between px-3 py-2.5 bg-surface border-b border-border cursor-pointer select-none"
        onClick={togglePanel}
      >
        <div className="flex items-center gap-2">
          {active > 0 && (
            <span className="w-4 h-4 rounded-full bg-primary flex items-center justify-center">
              <Loader2 size={10} className="text-white animate-spin"/>
            </span>
          )}
          <span className="text-xs font-semibold text-text">Processing</span>
          <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-border text-muted">
            {jobs.length}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {done > 0 && (
            <button
              onClick={e => { e.stopPropagation(); clearDone() }}
              className="text-[10px] text-muted hover:text-text px-1.5 py-0.5 rounded transition-colors"
            >
              Clear
            </button>
          )}
          {panelOpen
            ? <ChevronDown size={13} className="text-muted"/>
            : <ChevronUp   size={13} className="text-muted"/>
          }
        </div>
      </div>

      {/* Job list */}
      {panelOpen && (
        <div className="max-h-64 overflow-y-auto">
          {jobs.map(job => <JobRow key={job.id} job={job}/>)}
        </div>
      )}
    </div>
  )
}

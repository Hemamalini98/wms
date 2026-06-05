/**
 * ProcessingService
 *
 * Calls the FastAPI /process/* proxy endpoints.
 * FastAPI → PPH server (Python requests, no browser security restrictions).
 *
 * Browser never touches 10.1.1.69 directly — all traffic goes through
 * the existing WMS backend at /api/process/*.
 */

import apiClient from '@/api/client'
import {
  POLL_INTERVAL_MS,
  POLL_TIMEOUT_MS,
  STATUS_COMPLETE,
  STATUS_FAILED,
} from '@/config/processing'

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ProgressResult {
  job_id:   string
  status:   string
  progress: number
  message?: string
}

// ── Service ───────────────────────────────────────────────────────────────────

class ProcessingService {

  /**
   * Upload a file to the PPH server via the FastAPI proxy and start a job.
   * Returns the server-assigned job_id.
   */
  async startProcess(
    endpoint:     string,
    fileBlob:     Blob,
    fileName:     string,
    extraPayload?: Record<string, unknown>,
  ): Promise<string> {
    const form = new FormData()
    form.append('endpoint', endpoint)
    form.append('file',     fileBlob, fileName)
    form.append('payload',  JSON.stringify(extraPayload ?? {}))

    const res = await apiClient.post<{ job_id: string }>(
      '/process/start',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )

    return res.data.job_id
  }

  /**
   * Poll /process/progress/{job_id} until the job completes or fails.
   * Calls onProgress on each tick.
   */
  async pollProgress(
    jobId:      string,
    onProgress: (p: ProgressResult) => void,
  ): Promise<ProgressResult> {
    const start = Date.now()

    while (true) {
      if (Date.now() - start > POLL_TIMEOUT_MS) {
        throw new Error('Processing timed out after 10 minutes')
      }

      const res      = await apiClient.get<Record<string, unknown>>(`/process/progress/${jobId}`)
      const body     = res.data
      const rawStatus = String(body.status ?? '')
      const status    = rawStatus.toLowerCase()
      const progress  = Number(body.progress ?? body.percent ?? body.current ?? 0)

      // The status field sometimes contains a long error string like
      // "Failed: Unable to open HTML file …" — extract the human-readable part
      const errorMsg = rawStatus.includes(':')
        ? rawStatus.substring(rawStatus.indexOf(':') + 1).trim()
        : rawStatus

      const snapshot: ProgressResult = {
        job_id:   jobId,
        status:   rawStatus,
        progress,
        message:  (body.message as string | undefined) ?? errorMsg,
      }

      onProgress(snapshot)

      // Match complete/failed using startsWith so "Failed: …" strings are caught
      if (STATUS_COMPLETE.some(s => status === s || status.startsWith(s))) return snapshot
      if (STATUS_FAILED.some(s => status === s || status.startsWith(s))) {
        throw new Error(snapshot.message ?? `Job ${jobId} failed`)
      }

      await sleep(POLL_INTERVAL_MS)
    }
  }

  /**
   * Download the result ZIP for a completed job.
   * Returns a Blob and a filename derived from the Content-Disposition header.
   */
  async downloadZip(jobId: string): Promise<{ blob: Blob; filename: string }> {
    const res = await apiClient.get<Blob>(`/process/download/${jobId}`, {
      responseType: 'blob',
    })

    const cd       = (res.headers as Record<string, string>)['content-disposition'] ?? ''
    // const match    = cd.match(/filename[^;=\n]*=["']?([^"';\n]+)["']?/)
    let match=""
    const filename = match?.[1]?.trim() ?? `${jobId}.zip`

    return { blob: res.data, filename }
  }
}

export const processingService = new ProcessingService()

// ── Helpers ───────────────────────────────────────────────────────────────────

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Download a file from the WMS server and return it as a Blob.
 * Used to fetch the chapter file before forwarding it to the processing server.
 */
export async function fetchFileBlob(url: string): Promise<Blob> {
  const res = await fetch(url, { cache: 'no-store' })
  if (!res.ok) throw new Error(`Failed to fetch file: ${res.statusText}`)
  return res.blob()
}

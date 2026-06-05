import { useCallback } from 'react'
import apiClient from '@/api/client'
import { getProcessingConfig } from '@/config/processing'
import { processingService, fetchFileBlob } from '@/services/processingService'
import { useProcessingStore } from '@/store/processingStore'
import { useAuthStore } from '@/store/useAuthStore'
import { toast } from '@/store/useToastStore'
import type { FileRow } from '@/pages/ChapterFilePage'

interface UseProcessingQueueOptions {
  projectId:    number
  chapterName:  string
  stageName?:   string   // current chapter stage — used in backup filename
  onRefresh?:   () => void
}

let _uid = 0
function uid() { return `job-${++_uid}` }

export function useProcessingQueue({
  projectId, chapterName, stageName = '', onRefresh,
}: UseProcessingQueueOptions) {
  const { addJob, updateJob } = useProcessingStore()
  const currentUser = useAuthStore(s => s.user?.user_name ?? 'user')

  const handleProcess = useCallback(async (action: string, row: FileRow) => {
    const config = getProcessingConfig(action)
    if (!config) {
      toast.success(`${action} queued (no API configured)`)
      return
    }

    const jobUid    = uid()
    const subfolder = row.subfolder   // store results back to the same folder

    addJob({
      id:        jobUid,
      job_id:    null,
      file_name: row.file_name,
      action,
      status:    'queued',
      progress:  0,
    })
    // toast.success(`${action} started for ${row.file_name}`)

    try {
      // ── 1. Download source file from WMS ──────────────────────────────────
      updateJob(jobUid, { status: 'uploading', progress: 5 })
      const downloadUrl = `/api/uploads/${projectId}/chapter/${chapterName}/${subfolder}/${encodeURIComponent(row.file_name)}/download`
      const fileBlob    = await fetchFileBlob(downloadUrl)

      // ── 2. Send to processing server → get job_id ─────────────────────────
      updateJob(jobUid, { status: 'uploading', progress: 15 })
      const serverId = await processingService.startProcess(
        config.endpoint,
        fileBlob,
        row.file_name,
        config.payload,
      )
      updateJob(jobUid, { job_id: serverId, status: 'processing', progress: 20 })

      // ── 3. Poll progress ──────────────────────────────────────────────────
      await processingService.pollProgress(serverId, (p) => {
        const mapped = Math.max(20, Math.min(89, 20 + Math.round(p.progress * 0.69)))
        updateJob(jobUid, { progress: mapped })
      })

      // ── 4. Download result ZIP from PPH via proxy ─────────────────────────
      updateJob(jobUid, { status: 'processing', progress: 90 })
      const zipRes = await apiClient.get<Blob>(`/process/download/${serverId}`, {
        responseType: 'blob',
      })

      // ── 5. Extract ZIP and store files directly into chapter folder ───────
      updateJob(jobUid, { status: 'processing', progress: 95 })
      const form = new FormData()
      form.append('project_id',   String(projectId))
      form.append('chapter_name', chapterName)
      form.append('subfolder',    subfolder)
      form.append('stage_name',   stageName)
      form.append('process_name', action)
      form.append('uploaded_by',  currentUser)
      form.append('zip_file',     zipRes.data, `${serverId}.zip`)

      await apiClient.post('/process/extract-and-store', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      // ── 6. Done ───────────────────────────────────────────────────────────
      updateJob(jobUid, { status: 'completed', progress: 100 })
      // toast.success(`${action} complete — files saved to ${subfolder}`)
      onRefresh?.()

    } catch (err: unknown) {
      const msg = (err as Error)?.message ?? 'Processing failed'
      updateJob(jobUid, { status: 'failed', error: msg })
      // toast.error(`${action} failed: ${msg}`)
    }
  }, [projectId, chapterName, stageName, currentUser, onRefresh, addJob, updateJob])

  return { handleProcess }
}

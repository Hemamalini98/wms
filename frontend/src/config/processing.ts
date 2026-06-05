/**
 * Processing workflow configuration.
 * Maps UI action names → backend API endpoints and optional payloads.
 *
 * To add a new action: add an entry here — no other file needs changing.
 */

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ProcessingActionConfig {
  endpoint:    string
  method:      'GET' | 'POST'
  payload?:    Record<string, unknown>   // extra form fields sent alongside the file
  description: string
}

// ── Action → API mapping ──────────────────────────────────────────────────────

export const PROCESSING_API_CONFIG: Record<string, ProcessingActionConfig> = {
  'Structure Tag': {
    endpoint:    '/word-to-xml',
    method:      'POST',
    description: 'Convert Word document to structured XML',
  },
  'Metadata Check': {
    endpoint:    '/word-to-xml',
    method:      'POST',
    description: 'Check and validate document metadata',
  },
  'File Integrity': {
    endpoint:    '/validate',
    method:      'POST',
    description: 'Check file integrity and structure',
    payload: {
      run_validation:            'true',
      run_structuring:           'false',
      run_name_year_validation:  'false',
      run_gemini:                'false',
      citation_format:           'auto',
    },
  },
  'Validation Check': {
    endpoint:    '/validate',
    method:      'POST',
    description: 'Validate document structure and citations',
    payload: {
      source_style:              'Auto',
      target_style:              'APA',
      run_validation:            'true',
      run_structuring:           'true',
      run_name_year_validation:  'false',
      run_gemini:                'true',
      citation_format:           'auto',
    },
  },
  'AI QC': {
    endpoint:    '/bias-scan',
    method:      'POST',
    description: 'AI-powered quality control and bias scan',
  },
  'Reference Check': {
    endpoint:    '/validate',
    method:      'POST',
    description: 'Validate references and citations',
    payload: {
      source_style:  'Auto',
      target_style:  'APA',
      run_validation:'true',
      citation_format:'auto',
    },
  },
  'Accessibility Validation': {
    endpoint:    '/validate',
    method:      'POST',
    description: 'Check accessibility compliance',
    payload: { run_validation: 'true', run_structuring: 'true' },
  },
  'Generate EPUB': {
    endpoint:    '/word-to-xml',
    method:      'POST',
    description: 'Convert to EPUB format',
  },
  'Validate XML': {
    endpoint:    '/validate',
    method:      'POST',
    description: 'Validate XML structure',
    payload: { run_validation: 'true' },
  },
  'QC Checklist': {
    endpoint:    '/bias-scan',
    method:      'POST',
    description: 'Run full QC checklist',
  },
  'Markup Review': {
    endpoint:    '/validate',
    method:      'POST',
    description: 'Review document markup',
    payload: { run_structuring: 'true' },
  },
}

/**
 * Look up the API config for a given action name.
 * Returns null if the action has no API mapping (non-API actions are silently skipped).
 */
export function getProcessingConfig(actionName: string): ProcessingActionConfig | null {
  return PROCESSING_API_CONFIG[actionName] ?? null
}

// ── Server settings (set in .env) ─────────────────────────────────────────────

export const PROCESSING_SERVER = {
  baseUrl:  import.meta.env.VITE_PROCESSING_BASE_URL  ?? 'https://10.1.1.69',
  username: import.meta.env.VITE_PROCESSING_USERNAME  ?? 'admin',
  password: import.meta.env.VITE_PROCESSING_PASSWORD  ?? '',
}

export const POLL_INTERVAL_MS = 4_000         // check progress every 4 seconds
export const POLL_TIMEOUT_MS  = 10 * 60_000   // give up after 10 minutes

export const STATUS_COMPLETE = ['completed', 'complete', 'success', 'finished', 'done']
export const STATUS_FAILED   = ['failed', 'error', 'Failed', 'failure']

/**
 * File Manager Configuration
 *
 * Drives the enterprise file manager for the publishing workflow.
 */

// ── ChapterFile ────────────────────────────────────────────────────────────

export interface ChapterFileMetadata {
  dpi?:              number
  width?:            number
  height?:           number
  colorProfile?:     string
  xmlType?:          string
  validationStatus?: 'valid' | 'invalid' | 'pending'
  packageStatus?:    string
  reviewer?:         string
  reviewStatus?:     string
}

export type ProcessingStatus = 'idle' | 'queued' | 'processing' | 'completed' | 'failed'

export interface ChapterFile {
  id:               string
  folder:           FolderKey
  fileName:         string
  extension:        string
  size:             string
  sizeBytes:        number
  uploadedBy:       string
  uploadedOn:       string
  path:             string
  metadata?:        ChapterFileMetadata
  processingStatus: ProcessingStatus
}

export type FolderKey = 'manuscript' | 'art' | 'indesign' | 'proof' | 'xml' | 'misc' | 'backup'

export type ColumnKey =
  | 'fileName' | 'fileType' | 'size' | 'uploadedBy' | 'uploadedOn'
  | 'pageCount'
  | 'dimensions' | 'dpi' | 'colorProfile'
  | 'packageStatus'
  | 'reviewer' | 'reviewStatus'
  | 'xmlType' | 'validationStatus'

export interface ColumnDefinition { key: ColumnKey; header: string; width: number }

export const COLUMN_DEFINITIONS: Record<ColumnKey, ColumnDefinition> = {
  fileName:        { key: 'fileName',        header: 'File Name',      width: 240 },
  fileType:        { key: 'fileType',        header: 'Type',           width:  70 },
  pageCount:       { key: 'pageCount',       header: 'Pages',          width:  70 },
  size:            { key: 'size',            header: 'Size',           width:  80 },
  uploadedBy:      { key: 'uploadedBy',      header: 'Uploaded By',    width: 130 },
  uploadedOn:      { key: 'uploadedOn',      header: 'Uploaded On',    width: 140 },
  dimensions:      { key: 'dimensions',      header: 'Dimensions',     width: 100 },
  dpi:             { key: 'dpi',             header: 'DPI',            width:  60 },
  colorProfile:    { key: 'colorProfile',    header: 'Color Profile',  width: 110 },
  packageStatus:   { key: 'packageStatus',   header: 'Package Status', width: 120 },
  reviewer:        { key: 'reviewer',        header: 'Reviewer',       width: 120 },
  reviewStatus:    { key: 'reviewStatus',    header: 'Review Status',  width: 110 },
  xmlType:         { key: 'xmlType',         header: 'XML Type',       width: 100 },
  validationStatus:{ key: 'validationStatus',header: 'Validation',     width: 100 },
}

export interface FolderConfig { label: string; icon: string; allowUpload: boolean; allowDownload: boolean; columns: ColumnKey[] }

export const FOLDER_CONFIG: Record<FolderKey, FolderConfig> = {
  manuscript: { label:'Manuscript', icon:'FileText',      allowUpload:true,  allowDownload:true,  columns:['fileName','fileType','pageCount','size','uploadedBy','uploadedOn'] },
  art:        { label:'Art',        icon:'Image',         allowUpload:true,  allowDownload:true,  columns:['fileName','fileType','dimensions','dpi','colorProfile','size','uploadedBy','uploadedOn'] },
  indesign:   { label:'Indesign',   icon:'Layers',        allowUpload:true,  allowDownload:true,  columns:['fileName','fileType','packageStatus','size','uploadedBy','uploadedOn'] },
  proof:      { label:'Proof',      icon:'ClipboardCheck',allowUpload:true,  allowDownload:true,  columns:['fileName','fileType','reviewer','reviewStatus','size','uploadedBy','uploadedOn'] },
  xml:        { label:'XML',        icon:'Code2',         allowUpload:true,  allowDownload:true,  columns:['fileName','fileType','xmlType','validationStatus','size','uploadedBy','uploadedOn'] },
  misc:       { label:'Misc',       icon:'FolderOpen',    allowUpload:true,  allowDownload:true,  columns:['fileName','fileType','size','uploadedBy','uploadedOn'] },
  backup:     { label:'Backup',     icon:'Archive',       allowUpload:false, allowDownload:true,  columns:['fileName','fileType','size','uploadedOn'] },
}

/**
 * Processing rule — defines which actions appear in the Process menu.
 *
 * All specified conditions must match (AND logic).
 * Omitting a field means "match everything" for that dimension.
 *
 * To add a new rule: append an entry here — no other file needs changing.
 */
export interface ProcessingRule {
  /** Stage name patterns (partial, case-insensitive). Omit = all stages. */
  stages?:     string[]
  /** Folder labels to match (e.g. 'Manuscript', 'Art'). Omit = all folders. */
  folders?:    string[]
  /** File extensions WITHOUT dot (e.g. 'docx', 'xml'). Omit = all extensions. */
  extensions?: string[]
  /** Actions shown when this rule matches. */
  actions:     string[]
}

export const PROCESSING_RULES: ProcessingRule[] = [
  // ── Initiation ──────────────────────────────────────────────────────────────
  {
    stages:     ['initiation'],
    folders:    ['Manuscript'],
    extensions: ['docx', 'doc'],
    actions:    ['Structure Tag', 'Metadata Check', 'File Integrity'],
  },

  // ── Design ──────────────────────────────────────────────────────────────────
  {
    stages:     ['design'],
    folders:    ['Manuscript'],
    extensions: ['docx', 'doc'],
    actions:    ['Structure Tag', 'AI QC'],
  },

  // ── Editing ─────────────────────────────────────────────────────────────────
  {
    stages:     ['editing'],
    folders:    ['Manuscript'],
    extensions: ['docx', 'doc'],
    actions:    ['Structure Tag', 'Reference Check', 'Accessibility Validation', 'AI QC'],
  },

  // ── Copyediting ─────────────────────────────────────────────────────────────
  {
    stages:     ['copyediting'],
    folders:    ['Manuscript'],
    extensions: ['docx', 'doc'],
    actions:    ['Technical Editor', 'Grammar Check', 'Style Consistency', 'Reference Validation'],
  },

  // ── Production ──────────────────────────────────────────────────────────────
  {
    stages:     ['production'],
    folders:    ['Manuscript'],
    extensions: ['docx', 'doc'],
    actions:    ['Generate EPUB', 'Generate PDF'],
  },
  {
    stages:     ['production'],
    folders:    ['XML'],
    extensions: ['xml'],
    actions:    ['Validate XML', 'Package InDesign'],
  },

  // ── QC ──────────────────────────────────────────────────────────────────────
  {
    stages:     ['qc'],
    folders:    ['Manuscript'],
    extensions: ['docx', 'doc', 'pdf'],
    actions:    ['QC Checklist', 'Validation Check', 'Missing Elements'],
  },

  // ── Proofreading ────────────────────────────────────────────────────────────
  {
    stages:     ['proofreading'],
    folders:    ['Proof'],
    extensions: ['pdf', 'docx', 'doc'],
    actions:    ['Markup Review', 'Correction Tracking'],
  },
]

/**
 * Return the deduplicated list of actions for the given stage + folder + extension.
 *
 * @param stageName  Current chapter stage (partial match, case-insensitive)
 * @param folder     Active folder label, e.g. 'Manuscript'  (default: '' = match all)
 * @param fileExt    File extension without dot, e.g. 'docx'  (default: '' = match all)
 */
export function getProcessingActions(
  stageName: string,
  folder:    string = '',
  fileExt:   string = '',
): string[] {
  const stage = stageName.toLowerCase()
  const fld   = folder.toLowerCase()
  const ext   = fileExt.toLowerCase().replace(/^\./, '')

  const matched: string[] = []

  for (const rule of PROCESSING_RULES) {
    // Stage check — partial match either way
    if (rule.stages) {
      const stageMatch = rule.stages.some(
        s => stage.includes(s.toLowerCase()) || s.toLowerCase().includes(stage)
      )
      if (!stageMatch) continue
    }

    // Folder check — case-insensitive exact match
    if (rule.folders && fld) {
      const folderMatch = rule.folders.some(f => f.toLowerCase() === fld)
      if (!folderMatch) continue
    }

    // Extension check — case-insensitive exact match
    if (rule.extensions && ext) {
      const extMatch = rule.extensions.some(e => e.toLowerCase() === ext)
      if (!extMatch) continue
    }

    matched.push(...rule.actions)
  }

  // Deduplicate while preserving order
  return [...new Set(matched)]
}

export interface FileTypeIcon { icon: string; color: string }

export const FILE_TYPE_ICONS: Record<string, FileTypeIcon> = {
  doc:{ icon:'FileText',color:'#2B579A' }, docx:{ icon:'FileText',color:'#2B579A' },
  pdf:{ icon:'FileText',color:'#DC2626' }, txt:{ icon:'FileText',color:'#6B7280' },
  jpg:{ icon:'Image',color:'#D97706' },    jpeg:{ icon:'Image',color:'#D97706' },
  png:{ icon:'Image',color:'#059669' },    tif:{ icon:'Image',color:'#7C3AED' },
  tiff:{ icon:'Image',color:'#7C3AED' },   eps:{ icon:'Image',color:'#DB2777' },
  svg:{ icon:'Image',color:'#EA580C' },    bmp:{ icon:'Image',color:'#6B7280' },
  indd:{ icon:'Layers',color:'#FF3366' },  idml:{ icon:'Layers',color:'#FF3366' },
  xml:{ icon:'Code2',color:'#059669' },    zip:{ icon:'Archive',color:'#78716C' },
  default:{ icon:'File',color:'#9CA3AF' },
}

export function fileTypeIcon(ext: string): FileTypeIcon {
  return FILE_TYPE_ICONS[ext.toLowerCase().replace(/^\./, '')] ?? FILE_TYPE_ICONS['default']
}

"""
Upload / file-organisation configuration.

Edit this file to:
  - Add or rename chapter subfolders  (CHAPTER_SUBFOLDERS)
  - Map new file extensions to subfolders  (EXT_SUBFOLDER)
  - Update the sets of recognised extensions used during ZIP scanning
"""

# ── Chapter subfolder names ───────────────────────────────────────────────────
# Order matters: subfolders are displayed / created in this order.

CHAPTER_SUBFOLDERS: tuple[str, ...] = (
    "Manuscript",
    "Art",
    "Indesign",
    "Proof",
    "XML",
    "Misc",
)

# ── Extension → subfolder mapping ─────────────────────────────────────────────
# Keys must be lowercase. Any extension not listed here falls into "Misc".

EXT_SUBFOLDER: dict[str, str] = {
    # Manuscript
    ".doc":  "Manuscript",
    ".docx": "Manuscript",
    ".rtf":  "Manuscript",
    ".odt":  "Manuscript",

    # Art
    ".jpg":  "Art",
    ".jpeg": "Art",
    ".png":  "Art",
    ".tif":  "Art",
    ".tiff": "Art",
    ".eps":  "Art",
    ".svg":  "Art",
    ".bmp":  "Art",
    ".gif":  "Art",
    ".webp": "Art",

    # Indesign
    ".indd": "Indesign",
    ".idml": "Indesign",

    # Proof
    ".pdf":  "Proof",

    # XML
    ".xml":  "XML",
}

# ── Extension sets used during ZIP scanning (_scan helper) ────────────────────

CHAPTER_EXTS: frozenset[str] = frozenset({
    ".docx", ".doc",
})

IMAGE_EXTS: frozenset[str] = frozenset({
    ".png", ".jpg", ".jpeg", ".gif", ".tiff", ".tif",
    ".bmp", ".svg", ".webp", ".eps",
})

XML_EXTS: frozenset[str] = frozenset({".xml"})

DOC_EXTS: frozenset[str] = frozenset({
    ".pdf", ".txt", ".rtf", ".odt",
})

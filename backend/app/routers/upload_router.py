import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.init_db import get_db
from app.models.chapter_info import ChapterInfo
from app.models.client import Client
from app.models.project import Project
from app.models.stage_activity_master import StageActivityMaster
from app.models.stage_master import StageMaster
from app.models.workflow_master import WorkflowMaster

router = APIRouter(prefix="/uploads", tags=["Uploads"])

# Resolves to  backend/uploads/
UPLOAD_BASE = Path(__file__).resolve().parents[2] / "uploads"

# ── Config (edit app/config/upload_config.py to add/rename subfolders or extensions)
from app.config.upload_config import (   # noqa: E402
    CHAPTER_SUBFOLDERS,
    EXT_SUBFOLDER       as _EXT_SUBFOLDER,
    CHAPTER_EXTS,
    IMAGE_EXTS,
    XML_EXTS,
    DOC_EXTS,
)

# Matches: chapter1, ch01, ch_1, chapter_01, ch-02, chapter 3 …
_CHAPTER_RE = re.compile(r"ch(apter)?[_\-\s]?0*(\d+)", re.IGNORECASE)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", text).strip("_") or "unknown"


def _file_chapter_no(filename: str) -> Optional[int]:
    """Extract chapter number from any filename."""
    stem = Path(filename).stem
    match = _CHAPTER_RE.search(stem)
    if match:
        return int(match.group(2))
    # Fallback: any leading or standalone number
    m = re.search(r"(?<!\d)0*(\d+)(?!\d)", stem)
    return int(m.group(1)) if m else None


def _classify_file(ext: str) -> str:
    """Map a file extension to its destination subfolder."""
    return _EXT_SUBFOLDER.get(ext.lower(), "Misc")


def _create_chapter_folders(chapters_dir: Path) -> None:
    """Create all required subfolders inside a chapter directory."""
    for sf in CHAPTER_SUBFOLDERS:
        (chapters_dir / sf).mkdir(parents=True, exist_ok=True)


def _format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} B"
        size_bytes /= 1024  # type: ignore[assignment]
    return f"{size_bytes:.1f} TB"


def _organize_chapters(raw_dir: Path, project_dir: Path, repo_root: Path,
                       uploaded_by: str = "Unknown") -> dict:
    """
    Scan all files under raw_dir, group them by chapter number,
    create uploads/{customer}/{project}/chapters/chapter-{N}/ folder trees,
    and copy each file into the correct subfolder.

    Returns a dict:
      {
        chapter_no (int): {
          "folder": relative path string,
          "files":  [{"file_name", "subfolder", "path"}, …]
        }
      }
    """
    chapters_root = project_dir / "chapters"

    # Group every file by its chapter number
    by_chapter: dict[int, list[Path]] = {}
    unmatched:  list[Path] = []

    for f in sorted(raw_dir.rglob("*")):
        if not f.is_file():
            continue
        ch_no = _file_chapter_no(f.name)
        if ch_no is not None:
            by_chapter.setdefault(ch_no, []).append(f)
        else:
            unmatched.append(f)

    # Place unmatched files under chapter 0 → Misc
    if unmatched:
        by_chapter.setdefault(0, []).extend(unmatched)

    chapters_list: list[dict] = []

    for ch_no, files in sorted(by_chapter.items()):
        ch_folder = chapters_root / f"chapter-{ch_no}"
        _create_chapter_folders(ch_folder)

        # Build files grouped by subfolder: { "Manuscript": [...], "Art": [...], ... }
        grouped: dict[str, list[dict]] = {sf: [] for sf in CHAPTER_SUBFOLDERS}
        upload_ts = datetime.now(timezone.utc).isoformat()
        for f in files:
            subfolder  = _classify_file(f.suffix)
            dest       = ch_folder / subfolder / f.name
            shutil.copy2(f, dest)
            grouped[subfolder].append({
                "file_name":   f.name,
                "path":        dest.relative_to(repo_root.parent).as_posix(),
                "file_size":   _format_size(f.stat().st_size),
                "size_bytes":  f.stat().st_size,
                "uploaded_by": uploaded_by,
                "uploaded_on": upload_ts,
            })

        chapters_list.append({
            "chapter_name": f"chapter-{ch_no}",
            "folder":       ch_folder.relative_to(repo_root.parent).as_posix(),
            "files":        grouped,
        })

    return {"chapters": chapters_list}


def _scan(extract_dir: Path, repo_root: Path) -> dict:
    """Walk extract_dir and classify every file (for metadata/project.file_details)."""
    chapters:  list[dict] = []
    images:    list[dict] = []
    xml_files: list[dict] = []
    docs:      list[dict] = []

    # Extension sets come from app/config/upload_config.py
    # (IMAGE_EXTS, XML_EXTS, DOC_EXTS, CHAPTER_EXTS already imported at module level)

    for f in sorted(extract_dir.rglob("*")):
        if not f.is_file():
            continue
        ext      = f.suffix.lower()
        path_str = "/" + f.relative_to(repo_root).as_posix()
        ch_no    = _file_chapter_no(f.name)

        if ch_no is not None and ext in CHAPTER_EXTS:
            chapters.append({
                "chapter_no": ch_no,
                "file_name":  f.name,
                "path":       path_str,
            })
        elif ext in IMAGE_EXTS:
            images.append({"file_name": f.name, "path": path_str})
        elif ext in XML_EXTS:
            xml_files.append({"file_name": f.name, "path": path_str})
        elif ext in DOC_EXTS:
            docs.append({"file_name": f.name, "path": path_str})

    chapters.sort(key=lambda c: (c["chapter_no"] is None, c["chapter_no"] or 0))

    return {
        "total_chapters": len(chapters),
        "chapters":       chapters,
        "images":         images,
        "xml":            xml_files,
        "docs":           docs,
    }


def _resolve_workflow_start(
    db: Session, workflow_name: str
) -> tuple[Optional[str], Optional[str]]:
    first_wf = db.execute(
        select(WorkflowMaster)
        .where(WorkflowMaster.workflow_name == workflow_name)
        .where(WorkflowMaster.previous_stage.is_(None))
    ).scalars().first()

    if not first_wf:
        return None, None

    stage_name = first_wf.stage_name

    stage = db.execute(
        select(StageMaster).where(StageMaster.stage_name == stage_name)
    ).scalars().first()

    activity_name: Optional[str] = None
    if stage and stage.stage_activities:
        first_act = db.execute(
            select(StageActivityMaster)
            .where(StageActivityMaster.id == stage.stage_activities[0])
        ).scalars().first()
        if first_act:
            activity_name = first_act.stage_activity_name

    return stage_name, activity_name


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/{customer_code}/{project_code}", response_class=JSONResponse)
async def upload_project_zip(
    customer_code: str,
    project_code:  str,
    file:          UploadFile = File(...),
    project_id:    int        = Form(...),
    uploaded_by:   str        = Form("Unknown"),
    db:            Session    = Depends(get_db),
):
    if not (file.filename or "").lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    # Root project directory: uploads/{customer_code}/{project_code}/
    project_dir = UPLOAD_BASE / _slug(customer_code) / _slug(project_code)
    project_dir.mkdir(parents=True, exist_ok=True)

    # Save ZIP
    zip_path = project_dir / file.filename
    zip_path.write_bytes(await file.read())

    # Extract to uploads/{customer_code}/{project_code}/raw/{zip_stem}/
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            if zf.testzip() is not None:
                zip_path.unlink(missing_ok=True)
                raise HTTPException(status_code=422, detail="ZIP file is corrupted")
            raw_dir = project_dir / "inputs" / Path(file.filename).stem
            raw_dir.mkdir(parents=True, exist_ok=True)
            zf.extractall(raw_dir)
    except zipfile.BadZipFile:
        zip_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Invalid ZIP file")

    repo_root = UPLOAD_BASE.parent

    # Scan raw files for metadata
    metadata: dict = _scan(raw_dir, repo_root)
    metadata["zip_path"]       = "/" + zip_path.relative_to(repo_root).as_posix()
    metadata["extracted_path"] = "/" + raw_dir.relative_to(repo_root).as_posix()

    # ── Chapter-wise folder organisation ──────────────────────────────────────
    # Creates uploads/{customer}/{project}/chapters/chapter-{N}/{Manuscript|Art|...}/
    chapter_folders = _organize_chapters(raw_dir, project_dir, repo_root, uploaded_by)
    # Store under "chapter_folders" using the new list format
    metadata["chapter_folders"] = chapter_folders
    # Store the project directory so file-management endpoints can resolve paths
    metadata["project_dir"]     = project_dir.relative_to(repo_root.parent).as_posix()

    # Load project
    project = db.execute(select(Project).where(Project.id == project_id)).scalars().first()
    chapters_inserted = 0

    if project:
        project.file_details = metadata
        db.commit()

        stage_name:    Optional[str] = None
        activity_name: Optional[str] = None
        if project.workflow_name:
            stage_name, activity_name = _resolve_workflow_start(db, project.workflow_name)

        project_label = project.project_code or ""

        client = db.execute(
            select(Client).where(Client.id == project.client_id)
        ).scalars().first() if project.client_id else None
        client_label = client.division if client else ""

        existing: set[str] = {
            row.chapters
            for row in db.execute(
                select(ChapterInfo).where(ChapterInfo.project == project_label)
            ).scalars().all()
        }

        _COMPOSITION_MAP: dict[str, tuple[str, int]] = {
            "Low":    ("Low",    1),
            "Medium": ("Medium", 2),
            "High":   ("High",   3),
        }
        complexity, stage_level = _COMPOSITION_MAP.get(
            project.composition or "", ("Medium", 2)
        )

        for ch_info in chapter_folders.get("chapters", []):
            ch_name = ch_info["chapter_name"]          # e.g. "chapter-1"
            if ch_name == "chapter-0":
                continue  # skip misc/unmatched bucket
            # Extract numeric part: "chapter-1" → 1
            m = re.search(r"\d+$", ch_name)
            ch_no = int(m.group()) if m else None
            chapter_label = f"Chapter {ch_no}" if ch_no is not None else ch_name
            # Use primary Manuscript filename as chapter_title
            manuscript_files = ch_info["files"].get("Manuscript", [])
            chapter_title = (
                Path(manuscript_files[0]["file_name"]).stem
                if manuscript_files else chapter_label
            )

            if chapter_label in existing:
                continue

            db.add(ChapterInfo(
                client=client_label,
                project=project_label,
                chapters=chapter_label,
                chapter_title=chapter_title,
                project_manager_name=project.project_manager,
                due_date=project.due_date,
                stage_name=stage_name,
                current_stage_activity=activity_name,
                complexity_level=complexity,
                stage_level=stage_level,
                status="In-progress",
                published_status="Draft",
                workflow=project.workflow_name or "Workflow1",
            ))
            existing.add(chapter_label)
            chapters_inserted += 1

        db.commit()

    metadata["chapters_inserted"] = chapters_inserted
    return metadata


# ── File management: upload / download / replace ──────────────────────────────

def _patch_file_details(
    db:           Session,
    project_id:   int,
    chapter_name: str,
    subfolder:    str,
    new_entry:    dict,
    replace_filename: Optional[str] = None,
) -> None:
    """
    Update project.file_details in the DB after a file upload or replace.

    - replace_filename=None  → append new_entry to the subfolder list
    - replace_filename=str   → swap the matching file entry with new_entry
    """
    project = db.execute(select(Project).where(Project.id == project_id)).scalars().first()
    if not project:
        return

    fd = dict(project.file_details or {})
    chapters: list[dict] = fd.get("chapter_folders", {}).get("chapters", [])

    # Find the target chapter
    target = next((c for c in chapters if c["chapter_name"] == chapter_name), None)
    if target is None:
        return

    files: list[dict] = list(target["files"].get(subfolder, []))

    if replace_filename:
        # Swap the existing entry
        target["files"][subfolder] = [
            new_entry if f["file_name"] == replace_filename else f
            for f in files
        ]
    else:
        # Append (avoid duplicates by name)
        existing_names = {f["file_name"] for f in files}
        if new_entry["file_name"] not in existing_names:
            files.append(new_entry)
        else:
            files = [new_entry if f["file_name"] == new_entry["file_name"] else f for f in files]
        target["files"][subfolder] = files

    fd["chapter_folders"] = {"chapters": chapters}
    project.file_details   = fd
    flag_modified(project, "file_details")   # tell SQLAlchemy the JSON changed
    db.commit()


def _resolve_project_dir(db: Session, project_id: int) -> Path:
    """
    Return the project's upload folder.
    1. Prefer the stored project_dir from file_details.
    2. Fall back to reconstructing from division_code + project_code.
    """
    project = db.execute(select(Project).where(Project.id == project_id)).scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    # Try stored path first
    if project.file_details:
        pd = project.file_details.get("project_dir")
        if pd:
            candidate = UPLOAD_BASE.parent / pd
            if candidate.exists():
                return candidate

    # Fallback: reconstruct from project fields
    if project.project_code:
        # Try division_code as customer slug, then project_code
        customer_slug = _slug(project.division_code or "unknown")
        project_slug  = _slug(project.project_code)
        candidate     = UPLOAD_BASE / customer_slug / project_slug
        if candidate.exists():
            return candidate
        # Create the directory so uploads work even for new projects
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate

    raise HTTPException(
        status_code=404,
        detail="Cannot resolve project upload directory. Upload a ZIP first or ensure project_code is set."
    )


@router.post("/{project_id}/chapter/{chapter_name}/{subfolder}/upload",
             response_class=JSONResponse)
async def upload_chapter_file(
    project_id:  int,
    chapter_name: str,
    subfolder:   str,
    file:        UploadFile = File(...),
    uploaded_by: str        = Form("Unknown"),
    db:          Session    = Depends(get_db),
):
    """Add a new file to a chapter subfolder. Rejects if a file with the same name already exists."""
    if subfolder not in CHAPTER_SUBFOLDERS:
        raise HTTPException(400, f"subfolder must be one of {CHAPTER_SUBFOLDERS}")

    project_dir = _resolve_project_dir(db, project_id)
    dest_dir    = project_dir / "chapters" / chapter_name / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / (file.filename or "file")

    # ── Duplicate check ────────────────────────────────────────────────────
    if dest.exists():
        raise HTTPException(
            status_code=409,
            detail=f"'{dest.name}' already exists in {subfolder}. Use Replace to update it.",
        )

    dest.write_bytes(await file.read())

    upload_ts = datetime.now(timezone.utc).isoformat()
    entry = {
        "file_name":   dest.name,
        "path":        dest.relative_to(UPLOAD_BASE.parent).as_posix(),
        "file_size":   _format_size(dest.stat().st_size),
        "size_bytes":  dest.stat().st_size,
        "uploaded_by": uploaded_by,
        "uploaded_on": upload_ts,
    }

    # Persist new file entry into project.file_details so UI reflects it immediately
    _patch_file_details(db, project_id, chapter_name, subfolder, entry)

    return entry


from fastapi.responses import FileResponse as _FileResponse   # noqa: E402

@router.get("/{project_id}/chapter/{chapter_name}/{subfolder}/{filename}/download")
async def download_chapter_file(
    project_id:   int,
    chapter_name: str,
    subfolder:    str,
    filename:     str,
    db:           Session = Depends(get_db),
):
    """Stream a chapter file for download."""
    project_dir = _resolve_project_dir(db, project_id)
    file_path   = project_dir / "chapters" / chapter_name / subfolder / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    import mimetypes
    mime, _ = mimetypes.guess_type(str(file_path))
    headers = {
        "Content-Disposition":  f'inline; filename="{filename}"',
        "Cache-Control":         "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma":                "no-cache",
        "Expires":               "0",
    }
    return _FileResponse(path=str(file_path), filename=filename,
                         media_type=mime or "application/octet-stream",
                         headers=headers)


@router.post("/{project_id}/chapter/{chapter_name}/{subfolder}/{filename}/replace",
             response_class=JSONResponse)
async def replace_chapter_file(
    project_id:   int,
    chapter_name: str,
    subfolder:    str,
    filename:     str,
    file:         UploadFile = File(...),
    replaced_by:  str        = Form("Unknown"),
    stage_name:   str        = Form("unknown"),
    db:           Session    = Depends(get_db),
):
    """
    Replace a file in a chapter subfolder.
    Backup format (only when file size changes):
        {stem}_{stage_name}_{username}_{YYYYMMDD}_{HHMMSS}{ext}
    """
    project_dir = _resolve_project_dir(db, project_id)
    original    = project_dir / "chapters" / chapter_name / subfolder / filename
    if not original.exists():
        raise HTTPException(status_code=404, detail="Original file not found")

    # Read new file content first so we can compare sizes before overwriting
    new_bytes = await file.read()
    old_size  = original.stat().st_size
    new_size  = len(new_bytes)

    now        = datetime.now(timezone.utc)
    upload_ts  = now.isoformat()
    backup_name: Optional[str] = None

    # ── Backup (move) when file size differs, remove otherwise ───────────────
    if old_size != new_size:
        backup_dir = project_dir / "chapters" / chapter_name / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)

        date_str   = now.strftime("%Y%m%d")
        time_str   = now.strftime("%H%M%S")
        user_slug  = _slug(replaced_by)
        stage_slug = _slug(stage_name)
        backup_name = (
            f"{original.stem}_{stage_slug}_{user_slug}_{date_str}_{time_str}{original.suffix}"
        )
        # MOVE (not copy) — old file is gone from its original location
        shutil.move(str(original), backup_dir / backup_name)
    else:
        # Same size: just delete original so write_bytes creates a fresh file
        original.unlink()
        backup_name = None

    # ── Write new content to the ORIGINAL filename ─────────────────────────
    original.write_bytes(new_bytes)
    upload_ts = now.isoformat()

    new_entry = {
        "file_name":   filename,
        "path":        original.relative_to(UPLOAD_BASE.parent).as_posix(),
        "file_size":   _format_size(original.stat().st_size),
        "size_bytes":  original.stat().st_size,
        "uploaded_by": replaced_by,
        "uploaded_on": upload_ts,
    }

    # Persist updated file entry into project.file_details so UI reflects it immediately
    _patch_file_details(db, project_id, chapter_name, subfolder, new_entry,
                        replace_filename=filename)

    backup_info = (
        {
            "backup_name": backup_name,
            "backup_path": (
                project_dir / "chapters" / chapter_name / "backup" / backup_name
            ).relative_to(UPLOAD_BASE.parent).as_posix(),
            "size_changed": True,
            "old_size": old_size,
            "new_size": new_size,
        }
        if backup_name else
        {
            "backup_name": None,
            "size_changed": False,
            "old_size": old_size,
            "new_size": new_size,
        }
    )

    return {"file": new_entry, "backup": backup_info}


class _FileRef(BaseModel):
    subfolder: str
    file_name: str

class _BulkDownloadRequest(BaseModel):
    files: list[_FileRef]


@router.post("/{project_id}/chapter/{chapter_name}/bulk-download")
def bulk_download_files(
    project_id:   int,
    chapter_name: str,
    body:         _BulkDownloadRequest,
    db:           Session = Depends(get_db),
):
    """Stream a ZIP containing all requested files, or a single file directly."""
    from fastapi.responses import StreamingResponse, FileResponse as _FR
    import io, zipfile as _zf

    project_dir = _resolve_project_dir(db, project_id)

    if len(body.files) == 1:
        f    = body.files[0]
        path = project_dir / "chapters" / chapter_name / f.subfolder / f.file_name
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {f.file_name}")
        return _FR(path=str(path), filename=f.file_name,
                   headers={"Cache-Control": "no-store"})

    buf = io.BytesIO()
    with _zf.ZipFile(buf, mode="w", compression=_zf.ZIP_DEFLATED) as zf:
        for f in body.files:
            path = project_dir / "chapters" / chapter_name / f.subfolder / f.file_name
            if path.exists():
                zf.write(path, arcname=f"{f.subfolder}/{f.file_name}")

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{chapter_name}_files.zip"',
            "Cache-Control": "no-store",
        },
    )


@router.get("/{project_id}/chapter/{chapter_name}/backup-list",
            response_class=JSONResponse)
def list_backup_files(
    project_id:   int,
    chapter_name: str,
    db:           Session = Depends(get_db),
):
    """Return all files in the chapter's backup folder."""
    project_dir = _resolve_project_dir(db, project_id)
    backup_dir  = project_dir / "chapters" / chapter_name / "backup"
    if not backup_dir.exists():
        return {"files": []}
    files = []
    for f in sorted(backup_dir.iterdir()):
        if f.is_file():
            files.append({
                "file_name":   f.name,
                "path":        f.relative_to(UPLOAD_BASE.parent).as_posix(),
                "file_size":   _format_size(f.stat().st_size),
                "size_bytes":  f.stat().st_size,
                "uploaded_by": "—",
                "uploaded_on": datetime.fromtimestamp(
                    f.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            })
    return {"files": files}


@router.get("/{project_id}/chapter/{chapter_name}/backup/{filename}/download")
def download_backup_file(
    project_id:   int,
    chapter_name: str,
    filename:     str,
    db:           Session = Depends(get_db),
):
    from fastapi.responses import FileResponse
    project_dir = _resolve_project_dir(db, project_id)
    path = project_dir / "chapters" / chapter_name / "backup" / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Backup file not found")
    return FileResponse(
        path=str(path),
        filename=filename,
        headers={"Cache-Control": "no-store"},
    )

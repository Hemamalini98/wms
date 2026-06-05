"""
Processing proxy router.

Frontend → FastAPI /process/* → PPH server (https://10.1.1.69)

Python requests bypasses browser CORS/antivirus restrictions.
"""

import io
import os
import re
import zipfile as _zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
import urllib3
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.init_db import get_db
from app.routers.upload_router import (
    UPLOAD_BASE, _format_size, _patch_file_details, _resolve_project_dir,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

router = APIRouter(prefix="/process", tags=["Processing"])

# ── Config from environment ───────────────────────────────────────────────────

PPH_BASE_URL  = os.getenv("PPH_BASE_URL",  "https://10.1.1.69")
PPH_USERNAME  = os.getenv("PPH_USERNAME",  "admin")
PPH_PASSWORD  = os.getenv("PPH_PASSWORD",  "")

POLL_TIMEOUT  = 600   # seconds
POLL_INTERVAL = 4     # seconds

# ── PPH session (singleton per worker process) ────────────────────────────────

class _PPHSession:
    def __init__(self):
        self._session:    requests.Session = requests.Session()
        self._session.verify = False
        self._csrf:       Optional[str]    = None
        self._logged_in:  bool             = False

    # ── Login ─────────────────────────────────────────────────────────────────

    def login(self) -> None:
        url  = f"{PPH_BASE_URL}/login"
        resp = self._session.get(url, timeout=30)
        resp.raise_for_status()

        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp.text)
        if not match:
            raise RuntimeError("CSRF token not found on login page")
        self._csrf = match.group(1)

        resp = self._session.post(url, data={
            "username":   PPH_USERNAME,
            "password":   PPH_PASSWORD,
            "csrf_token": self._csrf,
        }, timeout=30)
        resp.raise_for_status()
        self._logged_in = True

    def _ensure_session(self) -> None:
        if not self._logged_in or not self._csrf:
            self.login()

    # ── Generic request ───────────────────────────────────────────────────────

    def call(
        self,
        endpoint: str,
        method:   str = "POST",
        files=None,
        data=None,
        json=None,
    ) -> requests.Response:
        self._ensure_session()
        headers = {"X-CSRF-Token": self._csrf}
        resp    = self._session.request(
            method  = method,
            url     = f"{PPH_BASE_URL}{endpoint}",
            headers = headers,
            files   = files,
            data    = data,
            json    = json,
            timeout = 300,
        )
        # Re-login on 401/403 and retry once
        if resp.status_code in (401, 403):
            self._logged_in = False
            self._csrf      = None
            self._ensure_session()
            resp = self._session.request(
                method  = method,
                url     = f"{PPH_BASE_URL}{endpoint}",
                headers = {"X-CSRF-Token": self._csrf},
                files   = files,
                data    = data,
                json    = json,
                timeout = 300,
            )
        resp.raise_for_status()
        return resp


_pph = _PPHSession()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/start")
async def start_processing(
    endpoint:  str        = Form(...),
    file:      UploadFile = File(...),
    payload:   str        = Form("{}"),   # JSON string of extra fields
):
    """
    Upload a file to the PPH server and start a processing job.
    Returns { job_id }.
    """
    import json as _json
    extra: dict = _json.loads(payload) if payload else {}

    file_bytes = await file.read()
    files_arg  = {
        "files": (file.filename, io.BytesIO(file_bytes),
                  file.content_type or "application/octet-stream")
    }

    try:
        resp = _pph.call(endpoint, method="POST", files=files_arg, data=extra or None)
    except requests.HTTPError as exc:
        raise HTTPException(status_code=502,
                            detail=f"PPH server error: {exc.response.status_code}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    body   = resp.json()
    job_id = body.get("job_id") or body.get("id") or body.get("task_id")
    if not job_id:
        raise HTTPException(status_code=502,
                            detail=f"Job ID not returned: {body.get('message', body)}")

    return JSONResponse({"job_id": str(job_id)})


@router.get("/progress/{job_id}")
def get_progress(job_id: str):
    """Poll the PPH server for job progress."""
    try:
        resp = _pph.call(f"/progress/{job_id}", method="GET")
    except requests.HTTPError as exc:
        raise HTTPException(status_code=502,
                            detail=f"PPH server error: {exc.response.status_code}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return JSONResponse(resp.json())


@router.get("/download/{job_id}")
def download_result(job_id: str):
    """Stream the result ZIP from the PPH server back to the browser."""
    try:
        resp = _pph.call(f"/download_zip/{job_id}", method="GET")
    except requests.HTTPError as exc:
        raise HTTPException(status_code=502,
                            detail=f"PPH server error: {exc.response.status_code}") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    filename = f"{job_id}.zip"
    cd       = resp.headers.get("content-disposition", "")
    if "filename=" in cd:
        m        = re.search(r'filename[^;=\n]*=(([\'"]).*?\2|[^;\n]*)', cd)
        filename = m.group(1).strip('"\'') if m else filename

    return StreamingResponse(
        io.BytesIO(resp.content),
        media_type = "application/zip",
        headers    = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control":       "no-store",
        },
    )


def _backup_name(filename: str, stage_name: str, process_name: str, user: str) -> str:
    """
    Build backup filename:
      {stem}_{stage}_{process}_{user}_{YYYYMMDD_HHMMSS}{ext}

    Example: chapter01_Editing_StructureTag_john_doe_20260604_142530.docx
    """
    import re as _re
    stem = Path(filename).stem
    ext  = Path(filename).suffix
    ts   = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    # Slugify the label parts so the filename stays safe
    def slug(s: str) -> str:
        return _re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_")
    return f"{stem}_{slug(stage_name)}_{slug(process_name)}_{slug(user)}_{ts}{ext}"


@router.post("/extract-and-store")
async def extract_and_store(
    project_id:   int        = Form(...),
    chapter_name: str        = Form(...),
    subfolder:    str        = Form(...),
    stage_name:   str        = Form(""),
    process_name: str        = Form(""),
    uploaded_by:  str        = Form("user"),
    zip_file:     UploadFile = File(...),
    db:           Session    = Depends(get_db),
):
    """
    Extract a result ZIP and save files into uploads/{project}/{chapter}/{subfolder}/.

    If a file with the same name already exists it is moved to the backup folder
    as  {stem}_{stage}_{process}_{user}_{datetime}{ext}  before being replaced.
    Updates project.file_details so the UI reflects the new files immediately.
    """
    project_dir = _resolve_project_dir(db, project_id)
    target_dir  = project_dir / "chapters" / chapter_name / subfolder
    backup_dir  = project_dir / "chapters" / chapter_name / "backup"
    target_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)

    raw       = await zip_file.read()
    stored    = []
    backed_up = []
    timestamp = datetime.now(timezone.utc).isoformat()

    with _zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for member in zf.namelist():
            if member.endswith("/") or Path(member).name.startswith("__"):
                continue

            filename = Path(member).name
            content  = zf.read(member)
            dest     = target_dir / filename

            # ── Backup existing file before overwriting ───────────────────
            if dest.exists():
                bk_name = _backup_name(filename, stage_name, process_name, uploaded_by)
                import shutil as _shutil
                _shutil.move(str(dest), backup_dir / bk_name)
                backed_up.append(bk_name)

            dest.write_bytes(content)

            entry = {
                "file_name":   filename,
                "path":        dest.relative_to(UPLOAD_BASE.parent).as_posix(),
                "file_size":   _format_size(len(content)),
                "size_bytes":  len(content),
                "uploaded_by": uploaded_by,
                "uploaded_on": timestamp,
            }
            _patch_file_details(db, project_id, chapter_name, subfolder, entry)
            stored.append(filename)

    return JSONResponse({
        "stored":    stored,
        "count":     len(stored),
        "backed_up": backed_up,
    })

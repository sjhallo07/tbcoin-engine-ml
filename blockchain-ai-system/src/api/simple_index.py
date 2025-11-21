"""Minimal Simple Repository API endpoints (HTML + JSON) per PEP 503/PEP 691.

This implements:
- GET /simple/           — project list (HTML or JSON via content negotiation)
- GET /simple/{project}/ — project detail with distribution files

Notes:
- We scan the local "dist/" directory to discover available files.
- Content negotiation prefers JSON when requested; defaults to HTML.
- We emit repository version meta as 1.4 to include latest additions.
"""

from __future__ import annotations

import hashlib
import html
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse


router = APIRouter()


REPO_VERSION = "1.4"
V1_JSON = "application/vnd.pypi.simple.v1+json"
V1_HTML = "application/vnd.pypi.simple.v1+html"


def _project_root() -> Path:
    # src/api/simple_index.py -> src -> project root
    return Path(__file__).resolve().parents[2]


def _dist_dir() -> Path:
    return _project_root() / "dist"


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _negotiate_format(request: Request) -> str:
    # 1) optional URL parameter override
    fmt = request.query_params.get("format")
    if fmt:
        # Only accept exact vendor types per spec
        if fmt in (V1_JSON, V1_HTML, "text/html"):
            return fmt
        # Fallback to JSON if explicitly requested but unknown
        return V1_JSON

    # 2) Accept header
    accept = request.headers.get("accept", "")
    if V1_JSON in accept:
        return V1_JSON
    if V1_HTML in accept or "text/html" in accept:
        return V1_HTML

    # Default to HTML for human-friendly browsing
    return V1_HTML


def _iter_projects(dist: Path) -> Iterable[str]:
    if not dist.exists():
        return []
    names: set[str] = set()
    for p in dist.iterdir():
        if not p.is_file():
            continue
        stem = p.name
        # Strip archives to inspect name-version
        for suf in (".whl", ".tar.gz", ".zip", ".tar.bz2"):
            if stem.endswith(suf):
                stem = stem[: -len(suf)]
                break
        # Wheel: name-version-... ; sdist: name-version
        parts = stem.split("-")
        if len(parts) < 2:
            continue
        pkg = parts[0]
        # Canonicalize underscores to hyphens
        pkg_norm = normalize(pkg)
        names.add(pkg_norm)
    return sorted(names)


def _file_hash_and_size(path: Path) -> Tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            size += len(chunk)
            h.update(chunk)
    return h.hexdigest(), size


def _upload_time(path: Path) -> str:
    ts = path.stat().st_mtime
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    # yyyy-mm-ddThh:mm:ss.ffffffZ, up to 6 digits
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _collect_files(dist: Path, project: str) -> List[Dict]:
    files: List[Dict] = []
    if not dist.exists():
        return files
    project_norm = normalize(project)
    for p in dist.iterdir():
        if not p.is_file():
            continue
        # Match files belonging to project by comparing normalized name prefix
        fname = p.name
        base = fname
        for suf in (".whl", ".tar.gz", ".zip", ".tar.bz2"):
            if base.endswith(suf):
                base = base[: -len(suf)]
                break
        parts = base.split("-")
        if not parts:
            continue
        candidate = normalize(parts[0].replace("_", "-"))
        if candidate != project_norm:
            continue
        sha256, size = _file_hash_and_size(p)
        rel_url = f"/files/{fname}"
        files.append(
            {
                "filename": fname,
                "url": rel_url,
                "hashes": {"sha256": sha256},
                "size": size,
                "upload-time": _upload_time(p),
            }
        )
    return files


@router.get("/simple", include_in_schema=False)
async def simple_no_slash() -> Response:
    # Redirect to trailing slash
    return RedirectResponse(url="/simple/", status_code=307)


@router.get("/simple/", include_in_schema=False)
async def simple_root(request: Request) -> Response:
    accept = _negotiate_format(request)
    dist = _dist_dir()
    projects = list(_iter_projects(dist))

    if accept == V1_JSON:
        payload = {
            "meta": {"api-version": REPO_VERSION},
            "projects": [{"name": name} for name in projects],
        }
        return JSONResponse(payload, media_type=V1_JSON)

    # HTML
    items = "\n".join(
        f'    <a href="/{html.escape(name)}/">{html.escape(name)}</a>' for name in projects
    )
    html_page = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "  <head>\n"
        f"    <meta name=\"pypi:repository-version\" content=\"{REPO_VERSION}\">\n"
        "    <meta charset=\"utf-8\">\n"
        "    <title>Simple Index</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"{items}\n"
        "  </body>\n"
        "</html>\n"
    )
    return HTMLResponse(html_page, media_type=V1_HTML)


@router.get("/simple/{project}", include_in_schema=False)
async def project_no_slash(project: str) -> Response:
    # Redirect to trailing slash
    return RedirectResponse(url=f"/simple/{normalize(project)}/", status_code=307)


@router.get("/simple/{project}/", include_in_schema=False)
async def simple_project_detail(project: str, request: Request) -> Response:
    accept = _negotiate_format(request)
    project = normalize(project)
    dist = _dist_dir()
    files = _collect_files(dist, project)

    if not files and project not in _iter_projects(dist):
        raise HTTPException(status_code=404, detail="Project not found")

    if accept == V1_JSON:
        payload = {
            "meta": {"api-version": REPO_VERSION},
            "name": project,
            "files": files,
            # Optional: versions omitted unless derivable reliably
        }
        return JSONResponse(payload, media_type=V1_JSON)

    # HTML with anchors and #sha256= fragments, and meta version
    anchors = []
    for f in files:
        href = f["url"] + f"#sha256={f['hashes']['sha256']}"
        text = f["filename"]
        anchors.append(f'    <a href="{html.escape(href)}">{html.escape(text)}</a>')
    items = "\n".join(anchors)
    html_page = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "  <head>\n"
        f"    <meta name=\"pypi:repository-version\" content=\"{REPO_VERSION}\">\n"
        "    <meta charset=\"utf-8\">\n"
        f"    <title>Index of {html.escape(project)}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"{items}\n"
        "  </body>\n"
        "</html>\n"
    )
    return HTMLResponse(html_page, media_type=V1_HTML)


@router.get("/files/{filename}", include_in_schema=False)
async def serve_file(filename: str) -> Response:
    # Serve distribution files from ./dist
    path = _dist_dir() / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    # Let Starlette/ASGI static file be avoided; return as FileResponse could be used,
    # but to keep dependencies minimal, stream manually with Response.
    data = path.read_bytes()
    # Best-effort content-type based on extension
    mtype = (
        "application/zip" if filename.endswith(".whl") else "application/gzip"
        if filename.endswith(".tar.gz")
        else "application/octet-stream"
    )
    return Response(content=data, media_type=mtype)

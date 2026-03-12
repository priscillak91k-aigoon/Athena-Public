"""
Athena Workspace Server
=======================
Local execution backend for the Athena Workspace IDE.
Provides file CRUD, command execution, and WebSocket terminal streaming.

Start: python athena-workspace/server.py
URL:   http://localhost:7337

Logs: athena-workspace/workspace.log
Health: http://localhost:7337/health
"""

import os
import sys
import json
import asyncio
import subprocess
import traceback
from pathlib import Path
from typing import Optional

import logging
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# ── Config ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

API_KEY = os.getenv("ATHENA_WORKSPACE_KEY", "athena-local-dev")
WORKSPACE_ROOT = Path(os.getenv("ATHENA_WORKSPACE_ROOT", str(ROOT)))
PORT = int(os.getenv("ATHENA_WORKSPACE_PORT", "7337"))

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE = Path(__file__).parent / "workspace.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("athena-workspace")
START_TIME = datetime.now()

# Directories that should not be shown in the file tree
HIDDEN_DIRS = {".git", ".aider.tags.cache.v4", "__pycache__", "node_modules",
               ".nosey_nutter", "multi_recon*"}

app = FastAPI(title="Athena Workspace", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7337", "http://127.0.0.1:7337"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    # Validate workspace root exists
    if not WORKSPACE_ROOT.exists():
        log.error(f"WORKSPACE_ROOT does not exist: {WORKSPACE_ROOT}")
        raise RuntimeError(f"Workspace root not found: {WORKSPACE_ROOT}")
    # Load persisted tasks
    _load_tasks()
    log.info(f"Athena Workspace started. Root: {WORKSPACE_ROOT} Port: {PORT}")
    log.info(f"Tasks loaded from disk: {len(TASK_LOG)}")


@app.on_event("shutdown")
async def on_shutdown():
    _save_tasks()
    log.info("Athena Workspace shut down cleanly.")


@app.get("/health")
def health_check():
    """System health — readable without API key so the UI can poll it."""
    uptime = (datetime.now() - START_TIME).total_seconds()
    # Log rotation — truncate if > 2MB
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 2_000_000:
        lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
        LOG_FILE.write_text("\n".join(lines[-500:]) + "\n", encoding="utf-8")
        log.info("workspace.log rotated (kept last 500 lines)")
    log_size = LOG_FILE.stat().st_size if LOG_FILE.exists() else 0
    recent_log = []
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
        recent_log = lines[-20:]
    return {
        "status": "ok",
        "uptime_seconds": round(uptime),
        "workspace_root": str(WORKSPACE_ROOT),
        "port": PORT,
        "log_file": str(LOG_FILE),
        "log_size_bytes": log_size,
        "recent_log": recent_log,
        "tasks_queued": len([t for t in TASK_LOG if t["status"] == "queued"]),
        "tasks_total": len(TASK_LOG),
    }


# ── Auth ─────────────────────────────────────────────────────────────────────
def verify_key(x_api_key: str = Header(default="")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True


# ── Models ───────────────────────────────────────────────────────────────────
class WriteRequest(BaseModel):
    content: str

class ExecRequest(BaseModel):
    command: str
    cwd: Optional[str] = None


# ── File Tree ─────────────────────────────────────────────────────────────────
def build_tree(path: Path, base: Path, depth: int = 0, max_depth: int = 4):
    if depth > max_depth:
        return None
    name = path.name
    if name.startswith(".") and depth > 0 and name not in {".context", ".obsidian", ".agent"}:
        return None
    if path.is_dir():
        if name in HIDDEN_DIRS or name.startswith("multi_recon"):
            return None
        children = []
        try:
            for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
                node = build_tree(child, base, depth + 1, max_depth)
                if node:
                    children.append(node)
        except PermissionError:
            pass
        return {"name": name, "type": "dir", "path": str(path.relative_to(base)), "children": children}
    else:
        ext = path.suffix.lower()
        if ext in {".exe", ".dll", ".pyc", ".db", ".sqlite", ".json"} and depth > 1:
            # Only show json at root-adjacent level
            if ext == ".json" and not name.endswith("_state.json"):
                return None
        size = path.stat().st_size if path.exists() else 0
        if size > 2_000_000:  # skip files > 2MB
            return None
        return {"name": name, "type": "file", "path": str(path.relative_to(base)), "ext": ext}


@app.get("/api/tree")
def get_tree(auth=Depends(verify_key)):
    tree = build_tree(WORKSPACE_ROOT, WORKSPACE_ROOT)
    return {"tree": tree}


# ── File Read/Write ───────────────────────────────────────────────────────────
def safe_path(rel: str) -> Path:
    p = (WORKSPACE_ROOT / rel).resolve()
    if not str(p).startswith(str(WORKSPACE_ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Path outside workspace")
    return p


@app.get("/api/file/{path:path}")
def read_file(path: str, auth=Depends(verify_key)):
    p = safe_path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if p.is_dir():
        raise HTTPException(status_code=400, detail="Path is a directory")
    try:
        content = p.read_text(encoding="utf-8", errors="replace")
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/file/{path:path}")
def write_file(path: str, body: WriteRequest, auth=Depends(verify_key)):
    p = safe_path(path)
    # Reject oversized payloads (> 5MB)
    if len(body.content.encode("utf-8")) > 5_000_000:
        raise HTTPException(status_code=413, detail="Content too large (max 5MB)")
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body.content, encoding="utf-8")
        log.info(f"WRITE {path} ({len(body.content)} chars)")
        return {"ok": True, "path": path}
    except Exception as e:
        log.error(f"WRITE FAILED {path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/file/{path:path}")
def delete_file(path: str, auth=Depends(verify_key)):
    p = safe_path(path)
    if not p.exists():
        raise HTTPException(status_code=404)
    try:
        p.unlink()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── One-shot Command Exec ─────────────────────────────────────────────────────
@app.post("/api/exec")
def execute(body: ExecRequest, auth=Depends(verify_key)):
    cwd = safe_path(body.cwd) if body.cwd else WORKSPACE_ROOT
    log.info(f"EXEC [{cwd.name}] $ {body.command[:120]}")
    try:
        result = subprocess.run(
            body.command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            log.warning(f"EXEC exit {result.returncode}: {body.command[:60]}")
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        log.error(f"EXEC TIMEOUT: {body.command[:60]}")
        return {"stdout": "", "stderr": "Command timed out after 120s", "returncode": -1}
    except Exception as e:
        log.error(f"EXEC ERROR: {traceback.format_exc()}")
        return {"stdout": "", "stderr": traceback.format_exc(), "returncode": -1}


# ── WebSocket Terminal (streaming) ────────────────────────────────────────────
@app.websocket("/ws/terminal")
async def terminal_ws(ws: WebSocket):
    await ws.accept()
    process = None
    try:
        # First message should be auth + optional command
        raw = await ws.receive_text()
        msg = json.loads(raw)

        if msg.get("key") != API_KEY:
            await ws.send_text(json.dumps({"type": "error", "data": "Auth failed"}))
            await ws.close()
            return

        cwd = str(WORKSPACE_ROOT)
        if msg.get("cwd"):
            cwd = str(safe_path(msg["cwd"]))

        cmd = msg.get("command", "")
        if not cmd:
            # Interactive shell
            cmd = "powershell.exe -NoLogo -NoProfile" if sys.platform == "win32" else "/bin/bash"

        process = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
        )

        async def read_output():
            while True:
                try:
                    chunk = await asyncio.wait_for(process.stdout.read(512), timeout=0.1)
                    if not chunk:
                        break
                    await ws.send_text(json.dumps({"type": "output", "data": chunk.decode("utf-8", errors="replace")}))
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    break
            rc = await process.wait()
            await ws.send_text(json.dumps({"type": "done", "returncode": rc}))

        read_task = asyncio.create_task(read_output())

        while True:
            try:
                inp = await asyncio.wait_for(ws.receive_text(), timeout=0.05)
                data = json.loads(inp)
                if data.get("type") == "input" and process.stdin:
                    process.stdin.write(data["data"].encode())
                    await process.stdin.drain()
                elif data.get("type") == "kill":
                    process.terminate()
                    break
            except asyncio.TimeoutError:
                if process.returncode is not None:
                    break
            except WebSocketDisconnect:
                break

        read_task.cancel()

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_text(json.dumps({"type": "error", "data": str(e)}))
        except Exception:
            pass
    finally:
        if process and process.returncode is None:
            try:
                process.terminate()
            except Exception:
                pass


# ── AI Task Queue (persistent) ───────────────────────────────────────────────
TASK_LOG: list[dict] = []
TASK_LOG_FILE = Path(__file__).parent / "task_log.json"


def _load_tasks():
    global TASK_LOG
    if TASK_LOG_FILE.exists():
        try:
            TASK_LOG = json.loads(TASK_LOG_FILE.read_text(encoding="utf-8"))
            log.info(f"Loaded {len(TASK_LOG)} tasks from disk")
        except Exception as e:
            log.error(f"Failed to load task log: {e}")
            TASK_LOG = []


def _save_tasks():
    try:
        TASK_LOG_FILE.write_text(json.dumps(TASK_LOG, indent=2), encoding="utf-8")
    except Exception as e:
        log.error(f"Failed to save task log: {e}")


class TaskRequest(BaseModel):
    task: str
    author: str = "lobotto"


@app.post("/api/task")
def add_task(body: TaskRequest, auth=Depends(verify_key)):
    entry = {"id": len(TASK_LOG), "task": body.task, "author": body.author,
             "time": datetime.now().isoformat(), "status": "queued"}
    TASK_LOG.append(entry)
    _save_tasks()
    log.info(f"TASK queued [{body.author}]: {body.task[:80]}")
    return {"ok": True, "id": entry["id"]}

@app.get("/api/tasks")
def get_tasks(auth=Depends(verify_key)):
    return {"tasks": TASK_LOG}

@app.patch("/api/task/{task_id}")
def update_task(task_id: int, status: str, auth=Depends(verify_key)):
    if task_id >= len(TASK_LOG):
        raise HTTPException(status_code=404)
    TASK_LOG[task_id]["status"] = status
    return {"ok": True}


# ── Serve Frontend ────────────────────────────────────────────────────────────
FRONTEND = Path(__file__).parent / "index.html"

@app.get("/")
def serve_ui():
    return FileResponse(str(FRONTEND))


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    import socket
    # Check if port is already in use
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("127.0.0.1", PORT)) == 0:
            print(f"⚠️  Port {PORT} already in use. Is Athena Workspace already running?")
            print(f"   Open http://localhost:{PORT} if so.")
            sys.exit(0)
    print(f"🚀 Athena Workspace | http://localhost:{PORT}")
    print(f"📁 Root: {WORKSPACE_ROOT}")
    print(f"📋 Log:  {LOG_FILE}")
    print(f"   Ctrl+C to stop\n")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")

#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DB_PATH = Path(os.environ.get("GOLDEN_DB", "golden.sqlite3")).resolve()
LOG_PATH = Path(os.environ.get("GOLDEN_LOG", "golden.log")).resolve()


def log(event: str, **fields: object) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": time.time(), "event": event, **fields}, ensure_ascii=False, sort_keys=True) + "\n")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, owner TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', created_at REAL NOT NULL)")
    conn.commit()
    return conn


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, object]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "GoldenRealApp/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        log("access", method=self.command, path=self.path, message=fmt % args)

    def _body(self) -> dict[str, str]:
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0") or "0"))
        ctype = self.headers.get("Content-Type", "")
        if "application/json" in ctype:
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
                return {str(k): str(v) for k, v in data.items()}
            except json.JSONDecodeError:
                return {}
        return {k: v[0] for k, v in parse_qs(raw.decode("utf-8")).items() if v}

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            json_response(self, 200, {"ok": True})
            return
        if path == "/":
            body = """<!doctype html><html><body><h1>Golden Real App</h1><form method="post" action="/api/v1/items"><input name="title" value="Real provided title"><input name="owner" value="human.operator@example.com"><button id="create-real-record" type="submit">Create real record</button></form><button id="refresh-list" data-endpoint="/api/v1/items">Refresh list</button></body></html>""".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/v1/items":
            with connect() as conn:
                rows = [dict(row) for row in conn.execute("SELECT id,title,owner,status FROM items ORDER BY id")]
            json_response(self, 200, {"items": rows})
            return
        if path.startswith("/api/v1/items/"):
            try:
                item_id = int(path.rsplit("/", 1)[-1])
            except ValueError:
                json_response(self, 404, {"code": "DOMAIN_NOT_FOUND"})
                return
            with connect() as conn:
                row = conn.execute("SELECT id,title,owner,status FROM items WHERE id=?", (item_id,)).fetchone()
            if not row:
                json_response(self, 404, {"code": "DOMAIN_NOT_FOUND"})
            else:
                json_response(self, 200, {"item": dict(row)})
            return
        json_response(self, 404, {"code": "NOT_FOUND"})

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/api/v1/items":
            json_response(self, 404, {"code": "NOT_FOUND"})
            return
        body = self._body()
        title = body.get("title", "").strip()
        owner = body.get("owner", "").strip()
        if not title or not owner:
            log("domain_validation_rejected", reason="missing_title_or_owner")
            json_response(self, 400, {"code": "DOMAIN_VALIDATION_FAILED"})
            return
        with connect() as conn:
            cur = conn.execute("INSERT INTO items(title,owner,status,created_at) VALUES (?,?,'draft',?)", (title, owner, time.time()))
            conn.commit()
            row = conn.execute("SELECT id,title,owner,status FROM items WHERE id=?", (int(cur.lastrowid),)).fetchone()
        log("domain_item_created", id=row["id"], owner=owner)
        json_response(self, 201, {"item": dict(row)})

    def do_PATCH(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            item_id = int(path.rsplit("/", 1)[-1])
        except ValueError:
            json_response(self, 404, {"code": "DOMAIN_NOT_FOUND"})
            return
        status = self._body().get("status", "approved").strip() or "approved"
        if status not in {"draft", "approved"}:
            log("domain_validation_rejected", reason="invalid_status", id=item_id)
            json_response(self, 400, {"code": "DOMAIN_VALIDATION_FAILED"})
            return
        with connect() as conn:
            if not conn.execute("SELECT id FROM items WHERE id=?", (item_id,)).fetchone():
                json_response(self, 404, {"code": "DOMAIN_NOT_FOUND"})
                return
            conn.execute("UPDATE items SET status=? WHERE id=?", (status, item_id))
            conn.commit()
            row = conn.execute("SELECT id,title,owner,status FROM items WHERE id=?", (item_id,)).fetchone()
        log("domain_item_updated", id=item_id, status=status)
        json_response(self, 200, {"item": dict(row)})


def main() -> int:
    port = int(os.environ.get("GOLDEN_PORT") or os.environ.get("CLAUDE_BACKEND_PORT") or os.environ.get("CLAUDE_FRONTEND_PORT") or "8765")
    connect().close()
    log("server_started", port=port, db=str(DB_PATH))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log("server_stopped", port=port)
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

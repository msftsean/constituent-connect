from __future__ import annotations

import argparse
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT
from .eval_runner import run_evaluations
from .models import to_dict
from .workflow import ConstituentConnectWorkflow


class ConstituentConnectHandler(BaseHTTPRequestHandler):
    workflow = ConstituentConnectWorkflow()
    packaged_web_root = files("constituent_connect").joinpath("web")
    built_web_root = PROJECT_ROOT / "frontend" / "dist"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json({"status": "healthy", "mode": "local-synthetic"})
            return
        if self.path == "/api/synthetic/inquiries":
            self._json({"items": self.workflow.catalog.sample_inquiries})
            return
        asset = "index.html" if self.path in {"/", "/index.html"} else self.path.lstrip("/")
        if asset.startswith(("/", "\\")) or ".." in Path(asset).parts:
            self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        web_root = self.built_web_root if self.built_web_root.is_dir() else self.packaged_web_root
        target = web_root.joinpath(asset)
        try:
            content = target.read_bytes()
        except (FileNotFoundError, IsADirectoryError):
            if web_root != self.packaged_web_root and asset != "index.html":
                target = self.packaged_web_root.joinpath(asset)
                try:
                    content = target.read_bytes()
                except (FileNotFoundError, IsADirectoryError):
                    self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
                    return
            else:
                self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
                return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
        }.get(Path(asset).suffix, "application/octet-stream")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        try:
            payload = self._read_json()
            if self.path == "/api/intake":
                inquiry = self.workflow.assess_intake(
                    payload.get("message", ""),
                    payload.get("channel", "web"),
                    payload.get("language"),
                )
                self._json(to_dict(inquiry))
                return
            if self.path == "/api/respond":
                result = self.workflow.process(
                    payload.get("message", ""),
                    payload.get("channel", "web"),
                    payload.get("language"),
                )
                self._json(to_dict(result))
                return
            approval_match = re.fullmatch(
                r"/api/responses/([^/]+)/approve", self.path
            )
            if approval_match:
                response = self.workflow.approve_response(
                    approval_match.group(1),
                    payload.get("reviewer", "local-human-reviewer"),
                    payload.get("edited_text"),
                    payload.get("decision", "approve"),
                )
                self._json(to_dict(response))
                return
            if self.path == "/api/cases":
                case = self.workflow.create_case(payload.get("response_id", ""))
                self._json(to_dict(case), HTTPStatus.CREATED)
                return
            if self.path == "/api/evals/run":
                report = run_evaluations()
                self._json(report, HTTPStatus.ACCEPTED)
                return
            self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self._json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("Request body is too large.")
        body = self.rfile.read(length)
        return json.loads(body or b"{}")

    def _json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[http] {self.address_string()} {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Constituent Connect UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), ConstituentConnectHandler)
    print(f"Constituent Connect running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()

"""HTTP server — web chat UI + JSON API on port 1203."""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .gateway import Gateway

log = logging.getLogger(__name__)

PORT = 1203
HOST = "127.0.0.1"
CHAT_UI_PATH = Path(__file__).parent / "chat_ui.html"


class BotHTTPHandler(SimpleHTTPRequestHandler):
    """Handles web chat UI and API endpoints."""

    gateway: Gateway  # set on the class by start_server()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/chat"):
            self._serve_chat_ui()
        elif path == "/api/personality":
            self._json_response(self.gateway.get_personality_info())
        elif path == "/api/health":
            self._json_response(self.gateway.health_check())
        elif path == "/api/history":
            qs = parse_qs(parsed.query)
            chat_id = qs.get("chat_id", ["web-default"])[0]
            messages = self.gateway.memory.get_history(chat_id)
            self._json_response({
                "messages": messages,
            })
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            self._handle_chat()
        else:
            self.send_error(404)

    def _handle_chat(self) -> None:
        """Process a chat message and return the response."""
        body = self._read_body()
        if body is None:
            return

        text = body.get("message", "").strip()
        chat_id = body.get("chat_id", "web-default")

        if not text:
            self._json_response({"error": "Empty message"}, status=400)
            return

        response = self.gateway.process_message(chat_id, text)
        self._json_response({
            "response": response.text,
            "tools_called": response.tools_called,
            "principles": response.principles,
            "memory_count": response.memory_count,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "duration_ms": response.duration_ms,
        })

    def _serve_chat_ui(self) -> None:
        """Serve the self-contained chat UI HTML."""
        if not CHAT_UI_PATH.exists():
            self.send_error(500, "chat_ui.html not found")
            return
        content = CHAT_UI_PATH.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _read_body(self) -> dict | None:
        """Read and parse JSON request body."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            self._json_response({"error": "Empty body"}, status=400)
            return None
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self._json_response({"error": "Invalid JSON"}, status=400)
            return None

    def _json_response(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        log.info(format, *args)


def _kill_stale_server(port: int) -> None:
    """Kill any existing process on the port before binding."""
    try:
        pids = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip()
        for pid in pids.splitlines():
            pid_int = int(pid)
            if pid_int != os.getpid():
                os.kill(pid_int, signal.SIGTERM)
    except (subprocess.CalledProcessError, OSError):
        pass


class ThreadedHTTPServer(HTTPServer):
    """HTTPServer that handles requests in threads."""

    allow_reuse_address = True

    def process_request(self, request, client_address) -> None:  # type: ignore[override]
        t = threading.Thread(target=self._handle, args=(request, client_address))
        t.daemon = True
        t.start()

    def _handle(self, request, client_address) -> None:  # type: ignore[no-untyped-def]
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)


def start_server(gateway: Gateway, port: int = PORT) -> ThreadedHTTPServer:
    """Start the HTTP server with the given gateway."""
    _kill_stale_server(port)

    BotHTTPHandler.gateway = gateway
    server = ThreadedHTTPServer((HOST, port), BotHTTPHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    log.info("Bot web server started at http://%s:%d/chat", HOST, port)
    return server

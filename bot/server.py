"""HTTP server — web chat UI + JSON API on port 1203."""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import threading
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    from .gateway import Gateway
    from .personality import PersonalityLoader
except ImportError:
    from gateway import Gateway  # type: ignore[no-redef]
    from personality import PersonalityLoader  # type: ignore[no-redef]

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
        elif path == "/api/personalities":
            self._handle_get_personalities()
        elif path == "/api/config":
            self._handle_get_config()
        elif path == "/api/conversations/export":
            self._handle_export_conversation(parsed)
        elif path == "/api/projects":
            self._handle_get_projects()
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            self._handle_chat()
        elif path == "/api/config":
            self._handle_post_config()
        elif path == "/api/conversations/new":
            self._handle_new_conversation()
        elif path == "/api/personality/reload":
            self._handle_personality_reload()
        elif path == "/api/projects/switch":
            self._handle_switch_project()
        else:
            self.send_error(404)

    def _handle_chat(self) -> None:
        """Process a chat message and return the response."""
        body = self._read_body()
        if body is None:
            return

        text = body.get("message", "").strip()
        conversation_id = body.get("conversation_id", "web-default")

        if not text:
            self._json_response({"error": "Empty message"}, status=400)
            return

        response = self.gateway.process_message(conversation_id, text)
        self._json_response({
            "response": response.text,
            "personality": self.gateway.personality.name,
            "tools_called": response.tools_called,
            "principles_active": response.principles,
            "memory_count": response.memory_count,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "duration_ms": response.duration_ms,
        })

    def _handle_get_personalities(self) -> None:
        """List available personalities from the personalities/ directory."""
        pdir = Path(__file__).parent.parent / "personalities"
        try:
            loader = PersonalityLoader(pdir)
            names = loader.list_personalities()
        except FileNotFoundError:
            names = []
        self._json_response({"personalities": names})

    def _handle_get_config(self) -> None:
        """Return current bot config."""
        self._json_response({
            "personality": self.gateway.personality.name,
            "model": self.gateway.llm.model,
            "ollama_url": self.gateway.llm.base_url,
        })

    def _handle_post_config(self) -> None:
        """Update bot config at runtime."""
        body = self._read_body()
        if body is None:
            return

        pdir = Path(__file__).parent.parent / "personalities"

        if "personality" in body:
            try:
                loader = PersonalityLoader(pdir)
                self.gateway.personality = loader.load(body["personality"])
                self.gateway.system_prompt = self.gateway.personality.system_prompt
                self.gateway.principles = self.gateway.personality.principles
            except FileNotFoundError:
                self._json_response(
                    {"error": f"Personality '{body['personality']}' not found"},
                    status=400,
                )
                return

        if "model" in body:
            self.gateway.llm.model = body["model"]
        if "ollama_url" in body:
            self.gateway.llm.base_url = body["ollama_url"].rstrip("/")

        self._json_response({
            "personality": self.gateway.personality.name,
            "model": self.gateway.llm.model,
            "ollama_url": self.gateway.llm.base_url,
        })

    def _handle_new_conversation(self) -> None:
        """Create a new conversation and return its ID."""
        conversation_id = f"web-{uuid.uuid4().hex[:12]}"
        self._json_response({"conversation_id": conversation_id})

    def _handle_get_projects(self) -> None:
        """List registered projects and the active project."""
        config = getattr(self.gateway, "config", None)
        if not config:
            self._json_response({"projects": [], "active_project": ""})
            return
        self._json_response({
            "projects": config.list_projects(),
            "active_project": config.active_project,
        })

    def _handle_personality_reload(self) -> None:
        """Re-read personality files from disk without restarting."""
        try:
            self.gateway.reload_personality()
            self._json_response({
                "status": "reloaded",
                "personality": self.gateway.personality.name,
                "principles": self.gateway.principles,
            })
        except FileNotFoundError as exc:
            self._json_response({"error": str(exc)}, status=404)

    def _handle_export_conversation(self, parsed) -> None:
        """Export a conversation as markdown."""
        qs = parse_qs(parsed.query)
        conversation_id = qs.get("conversation_id", [""])[0]
        if not conversation_id:
            self._json_response({"error": "Missing conversation_id"}, status=400)
            return
        markdown = self.gateway.memory.export_markdown(conversation_id)
        if not markdown:
            self._json_response({"error": "Conversation not found or empty"}, status=404)
            return
        body = markdown.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{conversation_id}.md"')
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _handle_switch_project(self) -> None:
        """Switch the active project."""
        body = self._read_body()
        if body is None:
            return
        slug = body.get("slug", "").strip()
        if not slug:
            self._json_response({"error": "Missing 'slug'"}, status=400)
            return
        config = getattr(self.gateway, "config", None)
        if not config:
            self._json_response({"error": "No config available"}, status=500)
            return
        if config.switch_project(slug):
            self._json_response({
                "active_project": config.active_project,
                "projects": config.list_projects(),
            })
        else:
            self._json_response(
                {"error": f"Project '{slug}' not registered"},
                status=404,
            )

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


def create_app(gateway: Gateway | None = None, port: int = PORT) -> ThreadedHTTPServer:
    """Create the HTTP server (without starting it).

    If no gateway is provided, a default one is created.
    """
    if gateway is None:
        gateway = Gateway()
    BotHTTPHandler.gateway = gateway
    return ThreadedHTTPServer((HOST, port), BotHTTPHandler)


def start_server(gateway: Gateway, port: int = PORT) -> ThreadedHTTPServer:
    """Start the HTTP server with the given gateway."""
    _kill_stale_server(port)

    server = create_app(gateway, port)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    log.info("Bot web server started at http://%s:%d/chat", HOST, port)
    return server


if __name__ == "__main__":
    import signal as _sig
    import sys as _sys

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

    try:
        from config import BotConfig  # type: ignore[no-redef]
    except ImportError:
        from bot.config import BotConfig  # type: ignore[no-redef,assignment]

    cfg = BotConfig.load()
    gw = Gateway(
        personality_name=cfg.personality_name,
        model=cfg.model_name,
        ollama_url=cfg.ollama_url,
    )
    srv = start_server(gw, port=cfg.server_port)

    def _shutdown(sig, frame):  # type: ignore[no-untyped-def]
        logging.info("Shutting down...")
        srv.shutdown()
        _sys.exit(0)

    _sig.signal(_sig.SIGINT, _shutdown)
    _sig.signal(_sig.SIGTERM, _shutdown)
    _sig.pause()

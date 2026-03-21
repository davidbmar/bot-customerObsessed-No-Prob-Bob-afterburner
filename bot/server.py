"""HTTP server — web chat UI + JSON API on port 1203."""

from __future__ import annotations

# Bootstrap: when run directly as `python3 bot/server.py`, ensure the parent
# directory is on sys.path so `bot.*` package imports resolve correctly.
import sys
from pathlib import Path as _Path

if __name__ == "__main__" and __package__ is None:
    _parent = str(_Path(__file__).resolve().parent.parent)
    if _parent not in sys.path:
        sys.path.insert(0, _parent)
    __package__ = "bot"

import base64
import json
import logging
import os
import signal
import struct
import subprocess
import threading
import wave

# Ignore SIGPIPE — prevents crash when external API clients (anthropic/openai)
# encounter broken pipes in threaded HTTP handlers
if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .gateway import Gateway
from .personality import PersonalityLoader

log = logging.getLogger(__name__)

PORT = 1203


def _classify_llm_error(exc: Exception) -> tuple[int, dict]:
    """Classify an LLM-related exception into an HTTP status and error body."""
    import httpx

    exc_type = type(exc).__name__
    detail = str(exc)

    # Anthropic auth error
    try:
        import anthropic
        if isinstance(exc, anthropic.AuthenticationError):
            return 401, {"error": "Invalid API key", "detail": detail}
    except ImportError:
        pass

    # Connection errors → 503
    if isinstance(exc, (ConnectionError, httpx.ConnectError, httpx.TimeoutException)):
        return 503, {"error": "LLM unreachable", "detail": detail}

    # OpenAI auth errors
    try:
        import openai
        if isinstance(exc, openai.AuthenticationError):
            return 401, {"error": "Invalid API key", "detail": detail}
    except ImportError:
        pass

    import traceback
    traceback.print_exc()
    return 500, {"error": str(exc)}
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
        elif path == "/api/llm/providers":
            self._handle_get_llm_providers()
        elif path == "/api/llm/config":
            self._handle_get_llm_config(parsed)
        elif path == "/api/auth/session":
            self._handle_auth_session_check()
        elif path == "/api/voice/voices":
            self._handle_get_voices()
        else:
            self.send_error(404)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            self._handle_chat()
        elif path == "/api/chat/stream":
            self._handle_chat_stream()
        elif path == "/api/config":
            self._handle_post_config()
        elif path == "/api/conversations/new":
            self._handle_new_conversation()
        elif path == "/api/personality/reload":
            self._handle_personality_reload()
        elif path == "/api/projects/switch":
            self._handle_switch_project()
        elif path == "/api/llm/switch":
            self._handle_llm_switch()
        elif path == "/api/llm/config":
            self._handle_post_llm_config()
        elif path == "/api/tools/save_discovery":
            self._handle_save_discovery()
        elif path == "/api/auth/google":
            self._handle_auth_google()
        elif path == "/api/auth/logout":
            self._handle_auth_logout()
        elif path == "/api/voice/transcribe":
            self._handle_voice_transcribe()
        elif path == "/api/voice/synthesize":
            self._handle_voice_synthesize()
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

        try:
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
        except Exception as e:
            status, error_data = _classify_llm_error(e)
            self._json_response(error_data, status=status)

    def _handle_chat_stream(self) -> None:
        """Stream a chat response as SSE events."""
        body = self._read_body()
        if body is None:
            return

        text = body.get("message", "").strip()
        conversation_id = body.get("conversation_id", "web-default")

        if not text:
            self._json_response({"error": "Empty message"}, status=400)
            return

        try:
            gen = self.gateway.process_message_stream(conversation_id, text)
        except Exception as e:
            status, error_data = _classify_llm_error(e)
            self._json_response(error_data, status=status)
            return

        # Send SSE headers
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        gateway_response = None
        try:
            while True:
                chunk = next(gen)
                event = json.dumps(chunk)
                self.wfile.write(f"data: {event}\n\n".encode())
                self.wfile.flush()
        except StopIteration as e:
            gateway_response = e.value
        except Exception as e:
            error_event = json.dumps({"type": "error", "error": str(e)})
            try:
                self.wfile.write(f"data: {error_event}\n\n".encode())
                self.wfile.flush()
            except Exception:
                pass
            return

        # Send done event with metadata
        if gateway_response:
            done_event = json.dumps({
                "type": "done",
                "response": gateway_response.text,
                "tools_called": gateway_response.tools_called,
                "principles_active": gateway_response.principles,
                "personality": self.gateway.personality.name,
                "memory_count": gateway_response.memory_count,
                "tokens": {
                    "input": gateway_response.input_tokens,
                    "output": gateway_response.output_tokens,
                },
                "duration_ms": gateway_response.duration_ms,
            })
            try:
                self.wfile.write(f"data: {done_event}\n\n".encode())
                self.wfile.flush()
            except Exception:
                pass

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

    def _handle_get_llm_providers(self) -> None:
        """Return LLM_PROVIDERS dict with active provider marked."""
        from .llm import LLM_PROVIDERS
        from .llm_config import get_active_provider

        active = getattr(self.gateway, "_provider_id", None) or get_active_provider()
        active_label = LLM_PROVIDERS.get(active, {}).get("label", active)
        result = {}
        for pid, pinfo in LLM_PROVIDERS.items():
            result[pid] = dict(pinfo, active=(pid == active))
        self._json_response({
            "providers": result,
            "active_provider": active,
            "active_label": active_label,
        })

    def _handle_llm_switch(self) -> None:
        """Switch active LLM provider + model."""
        body = self._read_body()
        if body is None:
            return
        provider_id = body.get("provider_id", "").strip()
        model = body.get("model", "").strip() or None
        if not provider_id:
            self._json_response({"error": "Missing 'provider_id'"}, status=400)
            return
        try:
            self.gateway.switch_provider(provider_id, model=model)
            self._json_response({
                "provider": provider_id,
                "model": self.gateway.llm.model,
                "status": "switched",
            })
        except ValueError as exc:
            self._json_response({"error": str(exc)}, status=400)

    def _handle_get_llm_config(self, parsed) -> None:
        """Return current provider config (base_url, model, has_key)."""
        from .llm_config import load_provider_config, get_active_provider

        qs = parse_qs(parsed.query)
        provider_id = qs.get("provider_id", [None])[0]
        if not provider_id:
            provider_id = getattr(self.gateway, "_provider_id", None) or get_active_provider()

        cfg = load_provider_config(provider_id)
        self._json_response({
            "provider_id": provider_id,
            "base_url": cfg["base_url"],
            "model": cfg["model"],
            "has_key": bool(cfg.get("api_key")),
        })

    def _handle_post_llm_config(self) -> None:
        """Save provider-specific config (api_key, base_url override)."""
        from .llm_config import save_provider_config

        body = self._read_body()
        if body is None:
            return
        provider_id = body.get("provider_id", "").strip()
        if not provider_id:
            self._json_response({"error": "Missing 'provider_id'"}, status=400)
            return
        config_data = {}
        if "base_url" in body:
            config_data["base_url"] = body["base_url"]
        if "model" in body:
            config_data["model"] = body["model"]
        if "api_key" in body:
            config_data["api_key"] = body["api_key"]
        save_provider_config(provider_id, config_data)
        self._json_response({"status": "saved", "provider_id": provider_id})

    def _handle_save_discovery(self) -> None:
        """Save conversation as a seed discovery document."""
        from .tools import tool_save_discovery

        body = self._read_body()
        if body is None:
            return

        project_slug = body.get("project_slug", "").strip()
        conversation_id = body.get("conversation_id", "").strip()

        if not project_slug:
            self._json_response({"error": "Missing 'project_slug'"}, status=400)
            return
        if not conversation_id:
            self._json_response({"error": "Missing 'conversation_id'"}, status=400)
            return

        history = self.gateway.memory.get_history(conversation_id)
        if not history:
            self._json_response({"error": "No conversation history found"}, status=404)
            return

        # Get active provider for metadata
        provider = getattr(self.gateway, "_provider_id", "unknown")

        # Format as structured seed doc with Problem/Users/Use Cases sections
        result = tool_save_discovery(
            slug=project_slug,
            structured=True,
            messages=[{"role": m["role"], "content": m["content"]} for m in history],
            provider=provider,
        )

        if "not found" in result.lower():
            self._json_response({"error": result}, status=404)
            return

        # Extract path from result like "Discovery notes saved to /path/to/file"
        path = result.split("saved to ")[-1] if "saved to" in result else result
        self._json_response({"ok": True, "path": path})

    # -- Auth endpoints --

    def _handle_auth_google(self) -> None:
        """Authenticate with a Google Sign-In JWT."""
        body = self._read_body()
        if body is None:
            return
        jwt_token = body.get("credential", "").strip()
        if not jwt_token:
            self._json_response({"error": "Missing credential"}, status=400)
            return
        try:
            from .auth import authenticate_google
            user_id, session_token, user_info = authenticate_google(jwt_token)
            self._json_response({
                "session_token": session_token,
                "user": user_info,
            })
        except ValueError as e:
            self._json_response({"error": str(e)}, status=401)
        except Exception as e:
            log.exception("Google auth error")
            self._json_response({"error": str(e)}, status=500)

    def _handle_auth_logout(self) -> None:
        """Invalidate a session token."""
        body = self._read_body()
        if body is None:
            return
        token = body.get("session_token", "").strip()
        if token:
            from .db import delete_auth_session
            delete_auth_session(token)
        self._json_response({"ok": True})

    def _handle_auth_session_check(self) -> None:
        """Check if a session token is still valid (GET with Authorization header)."""
        auth_header = self.headers.get("Authorization", "")
        token = ""
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        if not token:
            self._json_response({"valid": False}, status=401)
            return
        from .auth import authenticate_session_token
        result = authenticate_session_token(token)
        if result:
            _, user_info = result
            self._json_response({"valid": True, "user": user_info})
        else:
            self._json_response({"valid": False}, status=401)

    # -- Voice endpoints --

    def _handle_get_voices(self) -> None:
        """Return available TTS voices."""
        try:
            from .tts import list_voices
            self._json_response({"voices": list_voices()})
        except ImportError:
            self._json_response({"voices": [], "error": "TTS not installed"})

    def _handle_voice_transcribe(self) -> None:
        """Transcribe uploaded audio (base64 PCM or WAV)."""
        body = self._read_body()
        if body is None:
            return
        audio_b64 = body.get("audio", "")
        sample_rate = body.get("sample_rate", 48000)
        audio_format = body.get("format", "pcm")

        if not audio_b64:
            self._json_response({"error": "Missing audio data"}, status=400)
            return

        try:
            from .stt import transcribe
            audio_bytes = base64.b64decode(audio_b64)

            # If WAV format, extract PCM from WAV container
            if audio_format == "wav":
                with wave.open(BytesIO(audio_bytes), "rb") as wf:
                    sample_rate = wf.getframerate()
                    audio_bytes = wf.readframes(wf.getnframes())

            text, no_speech_prob, avg_logprob, timing = transcribe(audio_bytes, sample_rate)
            self._json_response({
                "text": text,
                "no_speech_prob": no_speech_prob,
                "avg_logprob": avg_logprob,
                "timing": timing,
            })
        except ImportError:
            self._json_response({"error": "STT not installed (pip install faster-whisper)"}, status=501)
        except Exception as e:
            log.exception("STT error")
            self._json_response({"error": str(e)}, status=500)

    def _handle_voice_synthesize(self) -> None:
        """Synthesize text to speech, return WAV audio."""
        body = self._read_body()
        if body is None:
            return
        text = body.get("text", "").strip()
        voice_id = body.get("voice_id", "")

        if not text:
            self._json_response({"error": "Missing text"}, status=400)
            return

        try:
            from .tts import synthesize, TARGET_RATE
            pcm_bytes = synthesize(text, voice_id)

            if not pcm_bytes:
                self._json_response({"error": "TTS produced no audio"}, status=500)
                return

            # Wrap PCM in WAV container for browser playback
            wav_buf = BytesIO()
            with wave.open(wav_buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # int16
                wf.setframerate(TARGET_RATE)
                wf.writeframes(pcm_bytes)

            wav_bytes = wav_buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(wav_bytes)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(wav_bytes)
        except ImportError:
            self._json_response({"error": "TTS not installed (pip install piper-tts)"}, status=501)
        except Exception as e:
            log.exception("TTS error")
            self._json_response({"error": str(e)}, status=500)

    def _serve_chat_ui(self) -> None:
        """Serve the self-contained chat UI HTML, injecting config."""
        if not CHAT_UI_PATH.exists():
            self.send_error(500, "chat_ui.html not found")
            return
        content = CHAT_UI_PATH.read_text()
        # Inject Google Client ID so the Sign-In button works
        google_client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        content = content.replace(
            "</head>",
            f'<script>window.__GOOGLE_CLIENT_ID__ = "{google_client_id}";</script>\n</head>',
        )
        content_bytes = content.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content_bytes)))
        self.end_headers()
        self.wfile.write(content_bytes)

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
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                self.handle_error(request, client_address)
            except Exception:
                pass
        finally:
            try:
                self.shutdown_request(request)
            except Exception:
                pass


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

    thread = threading.Thread(target=server.serve_forever, daemon=False)
    thread.start()

    log.info("Bot web server started at http://%s:%d/chat", HOST, port)
    return server


def main() -> None:
    """Entry point for running the server directly."""
    import signal as _sig

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")

    from .config import BotConfig
    from .db import init_db

    init_db()
    cfg = BotConfig.load()

    # Export auth env vars so the auth module picks them up
    if cfg.google_client_id:
        os.environ.setdefault("GOOGLE_CLIENT_ID", cfg.google_client_id)
    if cfg.allowed_emails:
        os.environ.setdefault("ALLOWED_EMAILS", cfg.allowed_emails)

    gw = Gateway(
        personality_name=cfg.personality_name,
        model=cfg.model_name,
        ollama_url=cfg.ollama_url,
        provider_id=cfg.llm_provider or None,
    )
    srv = start_server(gw, port=cfg.server_port)

    # Start Telegram polling if configured
    poller = None
    if cfg.telegram_enabled and cfg.telegram_token:
        from .polling import TelegramPoller
        poller = TelegramPoller(cfg.telegram_token, gw)
        if poller.health_check():
            poller.start()
            logging.info("Telegram polling enabled")
        else:
            logging.warning("Telegram token invalid — polling disabled")
            poller = None

    def _shutdown(sig, frame):  # type: ignore[no-untyped-def]
        logging.info("Shutting down...")
        if poller:
            poller.stop()
        srv.shutdown()
        sys.exit(0)

    _sig.signal(_sig.SIGINT, _shutdown)
    _sig.signal(_sig.SIGTERM, _shutdown)
    _sig.pause()


if __name__ == "__main__":
    main()

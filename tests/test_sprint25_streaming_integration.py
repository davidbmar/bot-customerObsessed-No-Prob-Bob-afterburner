"""Sprint 25 — Server-side streaming abort + concurrent request integration tests.

These tests verify:
1. Client disconnection during SSE streaming is handled gracefully
2. Aborting mid-stream doesn't crash the server or leave zombie threads
3. Concurrent/overlapping requests are handled cleanly
"""

from __future__ import annotations

import json
import socket
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from bot.gateway import Gateway, GatewayResponse
from bot.llm import LLMResponse, OllamaClient
from bot.server import create_app


def _find_free_port() -> int:
    """Find a free TCP port for the test server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def personalities_dir() -> Path:
    return Path(__file__).parent.parent / "personalities"


@pytest.fixture
def mock_llm_chat():
    def fake_chat(messages, system_prompt=None, tools=None):
        return LLMResponse(content="Mock response", duration_ms=10)

    with patch("bot.llm.OllamaClient.chat", side_effect=fake_chat):
        yield


@pytest.fixture
def gateway(personalities_dir, mock_llm_chat) -> Gateway:
    return Gateway(
        personality_name="customer-discovery",
        model="test-model",
        ollama_url="http://localhost:11434",
        personalities_dir=str(personalities_dir),
    )


@pytest.fixture
def test_server(gateway):
    """Start a real HTTP server on a random port for integration tests."""
    port = _find_free_port()
    server = create_app(gateway, port=port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server, port
    server.shutdown()
    server.server_close()


def _send_raw_http(port: int, method: str, path: str, body: dict | None = None) -> socket.socket:
    """Send a raw HTTP request and return the socket (for manual read/close)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect(("127.0.0.1", port))

    body_bytes = json.dumps(body).encode() if body else b""
    request = (
        f"{method} {path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode() + body_bytes

    sock.sendall(request)
    return sock


def _read_http_response(sock: socket.socket, timeout: float = 3.0) -> str:
    """Read full HTTP response from a socket."""
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data.decode("utf-8", errors="replace")


class TestStreamingAbortServerSide:
    """Verify server handles client disconnection during SSE streaming gracefully."""

    def test_server_survives_client_disconnect(self, gateway, test_server):
        """Client closing connection mid-stream should NOT crash the server.

        After the abort, the server should still accept new requests.
        """
        server, port = test_server

        # Set up a slow streaming generator that yields many chunks
        def slow_stream(messages, system_prompt=None, tools=None):
            for i in range(50):
                yield f"word{i} "
                time.sleep(0.05)
            return LLMResponse(content="full response", duration_ms=100)

        with patch.object(gateway.llm, "chat_stream", side_effect=slow_stream):
            # Start streaming request
            sock = _send_raw_http(port, "POST", "/api/chat/stream", {
                "message": "Hello",
                "conversation_id": "abort-test-1",
            })

            # Read just the HTTP headers + first few chunks
            sock.settimeout(2)
            try:
                partial = sock.recv(1024)
                assert b"200" in partial or b"text/event-stream" in partial
            except socket.timeout:
                pass

            # Abruptly close the connection (simulates browser abort)
            sock.close()

        # Give server a moment to clean up the broken pipe
        time.sleep(0.3)

        # Server should still work — send a regular (non-streaming) request
        sock2 = _send_raw_http(port, "GET", "/api/health", None)
        # For GET, no body needed — rewrite
        sock2.close()

        # Use a proper GET request
        sock3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock3.settimeout(3)
        sock3.connect(("127.0.0.1", port))
        sock3.sendall(
            f"GET /api/health HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n\r\n".encode()
        )
        response = _read_http_response(sock3)
        sock3.close()

        assert "200" in response
        assert "status" in response

    def test_abort_doesnt_leave_zombie_threads(self, gateway, test_server):
        """After aborting a stream, no extra threads should linger beyond baseline."""
        server, port = test_server

        baseline_threads = threading.active_count()

        def slow_stream(messages, system_prompt=None, tools=None):
            for i in range(100):
                yield f"chunk{i} "
                time.sleep(0.05)
            return LLMResponse(content="done", duration_ms=200)

        with patch.object(gateway.llm, "chat_stream", side_effect=slow_stream):
            sock = _send_raw_http(port, "POST", "/api/chat/stream", {
                "message": "test zombie",
                "conversation_id": "zombie-test",
            })
            # Read initial response
            sock.settimeout(1)
            try:
                sock.recv(512)
            except socket.timeout:
                pass
            sock.close()

        # Wait for the thread to notice the broken pipe and exit
        time.sleep(1.0)

        # Thread count should return close to baseline
        # (allow +2 for test framework overhead)
        current_threads = threading.active_count()
        assert current_threads <= baseline_threads + 2, (
            f"Possible zombie threads: baseline={baseline_threads}, "
            f"current={current_threads}"
        )

    def test_empty_message_returns_400(self, gateway, test_server):
        """Streaming endpoint rejects empty messages with 400."""
        server, port = test_server

        sock = _send_raw_http(port, "POST", "/api/chat/stream", {
            "message": "",
            "conversation_id": "empty-test",
        })
        response = _read_http_response(sock)
        sock.close()

        assert "400" in response
        assert "Empty message" in response


class TestConcurrentStreamingRequests:
    """Verify server handles overlapping/concurrent streaming requests cleanly."""

    def test_concurrent_streams_both_complete(self, gateway, test_server):
        """Two simultaneous streaming requests should both complete without error."""
        server, port = test_server

        results = [None, None]
        errors = [None, None]

        def fast_stream(messages, system_prompt=None, tools=None):
            for i in range(5):
                yield f"token{i} "
                time.sleep(0.02)
            return LLMResponse(content="done", duration_ms=50)

        def run_stream(idx, conv_id):
            try:
                sock = _send_raw_http(port, "POST", "/api/chat/stream", {
                    "message": f"concurrent test {idx}",
                    "conversation_id": conv_id,
                })
                response = _read_http_response(sock, timeout=5)
                sock.close()
                results[idx] = response
            except Exception as e:
                errors[idx] = str(e)

        with patch.object(gateway.llm, "chat_stream", side_effect=fast_stream):
            t1 = threading.Thread(target=run_stream, args=(0, "concurrent-a"))
            t2 = threading.Thread(target=run_stream, args=(1, "concurrent-b"))
            t1.start()
            t2.start()
            t1.join(timeout=10)
            t2.join(timeout=10)

        assert errors[0] is None, f"Stream 0 error: {errors[0]}"
        assert errors[1] is None, f"Stream 1 error: {errors[1]}"
        assert results[0] is not None, "Stream 0 got no response"
        assert results[1] is not None, "Stream 1 got no response"
        # Both should have 200 status
        assert "200" in results[0]
        assert "200" in results[1]

    def test_new_request_while_streaming_doesnt_crash(self, gateway, test_server):
        """Sending a non-streaming POST /api/chat while a stream is active
        should not crash the server."""
        server, port = test_server

        stream_started = threading.Event()
        stream_result = [None]

        def slow_stream(messages, system_prompt=None, tools=None):
            stream_started.set()
            for i in range(20):
                yield f"slow{i} "
                time.sleep(0.05)
            return LLMResponse(content="slow done", duration_ms=200)

        def run_slow_stream():
            try:
                sock = _send_raw_http(port, "POST", "/api/chat/stream", {
                    "message": "slow stream",
                    "conversation_id": "overlap-stream",
                })
                response = _read_http_response(sock, timeout=5)
                sock.close()
                stream_result[0] = response
            except Exception:
                pass

        with patch.object(gateway.llm, "chat_stream", side_effect=slow_stream):
            # Start a slow stream
            t = threading.Thread(target=run_slow_stream)
            t.start()

            # Wait until the stream has started yielding
            stream_started.wait(timeout=3)
            time.sleep(0.1)

            # Send a non-streaming chat request in parallel
            # (this uses the regular chat method, not stream)
            sock2 = _send_raw_http(port, "POST", "/api/chat", {
                "message": "quick question",
                "conversation_id": "overlap-chat",
            })
            chat_response = _read_http_response(sock2, timeout=5)
            sock2.close()

            t.join(timeout=10)

        # The non-streaming chat should get a 200 response
        assert "200" in chat_response
        assert "Mock response" in chat_response

    def test_server_healthy_after_concurrent_abuse(self, gateway, test_server):
        """After multiple concurrent streams (some aborted), server remains healthy."""
        server, port = test_server

        def fast_stream(messages, system_prompt=None, tools=None):
            for i in range(10):
                yield f"t{i} "
                time.sleep(0.01)
            return LLMResponse(content="ok", duration_ms=20)

        def fire_and_abort(conv_id):
            try:
                sock = _send_raw_http(port, "POST", "/api/chat/stream", {
                    "message": f"stress {conv_id}",
                    "conversation_id": conv_id,
                })
                sock.settimeout(0.1)
                try:
                    sock.recv(256)
                except socket.timeout:
                    pass
                sock.close()
            except Exception:
                pass

        with patch.object(gateway.llm, "chat_stream", side_effect=fast_stream):
            threads = []
            for i in range(5):
                t = threading.Thread(target=fire_and_abort, args=(f"stress-{i}",))
                threads.append(t)
                t.start()

            for t in threads:
                t.join(timeout=5)

        # Wait for cleanup
        time.sleep(0.5)

        # Server should still respond to health check
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect(("127.0.0.1", port))
        sock.sendall(
            f"GET /api/health HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n\r\n".encode()
        )
        response = _read_http_response(sock)
        sock.close()

        assert "200" in response
        assert "status" in response


class TestStreamingGatewayAbortBehavior:
    """Unit tests for gateway-level streaming abort behavior."""

    def test_generator_can_be_abandoned(self, gateway):
        """Abandoning a gateway stream generator mid-iteration shouldn't raise."""
        def slow_stream(messages, system_prompt=None, tools=None):
            for i in range(100):
                yield f"word{i} "
            return LLMResponse(content="full", duration_ms=50)

        with patch.object(gateway.llm, "chat_stream", side_effect=slow_stream):
            gen = gateway.process_message_stream("abandon-test", "Hi")
            # Only consume first 3 chunks
            for _ in range(3):
                chunk = next(gen)
                assert chunk["type"] == "token"
            # Abandon the generator (simulates what happens on abort)
            gen.close()

    def test_stream_error_mid_generation(self, gateway):
        """If LLM raises mid-stream, the generator should propagate the error."""
        def error_stream(messages, system_prompt=None, tools=None):
            yield "start "
            raise RuntimeError("LLM connection lost")

        with patch.object(gateway.llm, "chat_stream", side_effect=error_stream):
            gen = gateway.process_message_stream("error-test", "Hi")
            chunk = next(gen)
            assert chunk["content"] == "start "
            with pytest.raises(RuntimeError, match="LLM connection lost"):
                next(gen)

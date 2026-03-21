"""Telegram polling transport — long-polls getUpdates and routes to Gateway."""

from __future__ import annotations

import logging
import threading
import time

import httpx

from .gateway import Gateway

log = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}"


class TelegramPoller:
    """Polls Telegram getUpdates and sends responses via sendMessage."""

    def __init__(self, bot_token: str, gateway: Gateway) -> None:
        self.token = bot_token
        self.gateway = gateway
        self.api_url = TELEGRAM_API.format(token=bot_token)
        self._client = httpx.Client(timeout=60.0)
        self._offset = 0
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start polling in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        log.info("Telegram polling started")

    def stop(self) -> None:
        """Stop polling."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        log.info("Telegram polling stopped")

    def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                updates = self._get_updates()
                for update in updates:
                    self._handle_update(update)
            except httpx.HTTPError as exc:
                log.error("Telegram poll error: %s", exc)
                time.sleep(5)
            except Exception:
                log.exception("Unexpected error in poll loop")
                time.sleep(5)

    def _get_updates(self) -> list[dict]:
        """Long-poll for new messages."""
        resp = self._client.get(
            f"{self.api_url}/getUpdates",
            params={"offset": self._offset, "timeout": 30},
        )
        resp.raise_for_status()
        data = resp.json()
        results = data.get("result", [])
        if results:
            self._offset = results[-1]["update_id"] + 1
        return results

    def _handle_update(self, update: dict) -> None:
        """Process a single update from Telegram."""
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))

        if not text or not chat_id:
            return

        # Handle /start command
        if text.strip() == "/start":
            welcome = (
                "Welcome! I'm your Afterburner customer discovery bot.\n\n"
                "Tell me about the problem you're trying to solve, "
                "and I'll help you think through your users, use cases, "
                "and success criteria.\n\n"
                "Just type naturally — no special commands needed."
            )
            self._send_message(chat_id, welcome)
            return

        # Skip other slash commands that aren't for us
        if text.startswith("/") and not text.startswith("/ask"):
            return

        # Strip /ask prefix if present
        if text.startswith("/ask "):
            text = text[5:]

        log.info("Telegram [%s]: %s", chat_id, text[:80])

        # Process through gateway — Telegram is read-only (no write tools)
        response = self.gateway.process_message(f"telegram-{chat_id}", text, read_only=True)

        # Send response
        self._send_message(chat_id, response.text)

    def _send_message(self, chat_id: str, text: str) -> None:
        """Send a message to a Telegram chat."""
        try:
            self._client.post(
                f"{self.api_url}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                },
            )
        except httpx.HTTPError as exc:
            log.error("Failed to send Telegram message: %s", exc)

    def health_check(self) -> bool:
        """Verify bot token is valid."""
        try:
            resp = self._client.get(f"{self.api_url}/getMe")
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

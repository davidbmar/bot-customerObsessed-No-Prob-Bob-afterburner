#!/usr/bin/env python3
"""CLI for afterburner-customer-bot.

Usage:
    afterburner-bot start                     # Start web server + Telegram polling
    afterburner-bot chat                      # Interactive CLI chat
    afterburner-bot chat "message"            # Single message
    afterburner-bot chat --personality NAME   # Use specific personality
    afterburner-bot status                    # Check health
    afterburner-bot evaluate NAME             # Run evaluation scenarios (Phase 2)
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys

from bot.config import BotConfig
from bot.gateway import Gateway
from bot.polling import TelegramPoller
from bot.server import start_server


def cmd_start(args: argparse.Namespace) -> None:
    """Start the bot server + optional Telegram polling."""
    config = BotConfig.load()
    personality = args.personality or config.personality

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("bot")

    log.info("Loading personality: %s", personality)
    gateway = Gateway(
        personality_name=personality,
        model=config.model,
        ollama_url=config.ollama_url,
    )

    # Start web server
    port = args.port or config.server_port
    server = start_server(gateway, port=port)
    log.info("Web chat: http://127.0.0.1:%d/chat", port)

    # Start Telegram polling if configured
    poller = None
    if config.telegram_enabled and config.telegram_token:
        poller = TelegramPoller(config.telegram_token, gateway)
        if poller.health_check():
            poller.start()
            log.info("Telegram polling active")
        else:
            log.warning("Telegram bot token invalid — polling disabled")
    else:
        log.info("Telegram polling disabled (no token configured)")

    # Wait for Ctrl+C
    def shutdown(sig, frame):  # type: ignore[no-untyped-def]
        log.info("Shutting down...")
        if poller:
            poller.stop()
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    signal.pause()


def cmd_chat(args: argparse.Namespace) -> None:
    """Interactive or single-message CLI chat."""
    config = BotConfig.load()
    personality = args.personality or config.personality

    gateway = Gateway(
        personality_name=personality,
        model=config.model,
        ollama_url=config.ollama_url,
    )

    chat_id = "cli-session"

    # Single message mode
    if args.message:
        message = " ".join(args.message)
        resp = gateway.process_message(chat_id, message)
        print(resp.text)
        return

    # Interactive mode
    print(f"Customer Discovery Agent ({config.model} · {personality})")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not text or text.lower() in ("quit", "exit", "q"):
            break

        resp = gateway.process_message(chat_id, text)
        print(f"\nBot: {resp.text}\n")

        if resp.tools_called:
            for tc in resp.tools_called:
                print(f"  [tool: {tc['name']}]")
            print()


def cmd_status(args: argparse.Namespace) -> None:
    """Check system health."""
    config = BotConfig.load()
    gateway = Gateway(
        personality_name=config.personality,
        model=config.model,
        ollama_url=config.ollama_url,
    )
    health = gateway.health_check()
    for key, val in health.items():
        status = "ok" if val not in ("unavailable",) else "FAIL"
        print(f"  {key}: {val} {'✓' if status == 'ok' else '✗'}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="afterburner-bot",
        description="Afterburner Customer Discovery Bot",
    )
    sub = parser.add_subparsers(dest="command")

    # start
    p_start = sub.add_parser("start", help="Start web server + Telegram polling")
    p_start.add_argument("--personality", "-p", help="Personality name")
    p_start.add_argument("--port", type=int, help="Web server port")

    # chat
    p_chat = sub.add_parser("chat", help="Interactive or single-message chat")
    p_chat.add_argument("message", nargs="*", help="Message (omit for interactive)")
    p_chat.add_argument("--personality", "-p", help="Personality name")

    # status
    sub.add_parser("status", help="Check system health")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "chat":
        cmd_chat(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

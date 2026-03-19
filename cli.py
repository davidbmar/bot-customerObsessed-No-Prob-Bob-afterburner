#!/usr/bin/env python3
"""CLI for afterburner-customer-bot.

Usage:
    python3 cli.py start                     # Start web server on port 1203
    python3 cli.py chat                      # Interactive CLI chat loop
    python3 cli.py status                    # Show bot status
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys

import httpx

from bot.config import BotConfig
from bot.memory import ConversationMemory
from bot.server import start_server


def cmd_start(args: argparse.Namespace) -> None:
    """Start the web server and print the URL."""
    config = BotConfig.load()
    personality = args.personality or config.personality

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("bot")

    # Import Gateway here to avoid import errors when just running status
    from bot.gateway import Gateway

    log.info("Loading personality: %s", personality)
    gateway = Gateway(
        personality_name=personality,
        model=config.model,
        ollama_url=config.ollama_url,
    )

    port = args.port or config.server_port
    server = start_server(gateway, port=port)
    url = f"http://127.0.0.1:{port}/chat"
    log.info("Web chat: %s", url)
    print(f"Server running at {url}")

    def shutdown(sig, frame):  # type: ignore[no-untyped-def]
        log.info("Shutting down...")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    signal.pause()


def cmd_chat(args: argparse.Namespace) -> None:
    """Interactive CLI chat loop — reads from stdin, prints responses."""
    config = BotConfig.load()
    personality = args.personality or config.personality

    from bot.gateway import Gateway

    gateway = Gateway(
        personality_name=personality,
        model=config.model,
        ollama_url=config.ollama_url,
    )

    chat_id = "cli-session"

    print(f"Afterburner Bot ({config.model} / {personality})")
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


def cmd_status(args: argparse.Namespace) -> None:
    """Show bot status: server reachability, personality, conversation count."""
    config = BotConfig.load()
    memory = ConversationMemory()

    conversations = memory.list_conversations()

    # Check if server is running
    port = config.server_port
    server_status = "not running"
    try:
        r = httpx.get(f"http://127.0.0.1:{port}/api/health", timeout=2.0)
        if r.status_code == 200:
            server_status = "running"
    except (httpx.ConnectError, httpx.TimeoutException):
        pass

    print(f"  Server:        {server_status} (port {port})")
    print(f"  Personality:   {config.personality}")
    print(f"  Model:         {config.model}")
    print(f"  Conversations: {len(conversations)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="afterburner-bot",
        description="Afterburner Customer Discovery Bot",
    )
    sub = parser.add_subparsers(dest="command")

    # start
    p_start = sub.add_parser("start", help="Start web server on port 1203")
    p_start.add_argument("--personality", "-p", help="Personality name")
    p_start.add_argument("--port", type=int, help="Web server port")

    # chat
    p_chat = sub.add_parser("chat", help="Interactive CLI chat loop")
    p_chat.add_argument("--personality", "-p", help="Personality name")

    # status
    sub.add_parser("status", help="Show bot status")

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

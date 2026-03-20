"""Entry point: python3 -m bot"""

import logging
import signal
import sys

from .config import BotConfig
from .gateway import Gateway
from .server import start_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")


def main() -> None:
    cfg = BotConfig.load()
    gateway = Gateway(
        personality_name=cfg.personality_name,
        model=cfg.model_name,
        ollama_url=cfg.ollama_url,
    )
    server = start_server(gateway, port=cfg.server_port)

    def _shutdown(sig, frame):  # type: ignore[no-untyped-def]
        logging.info("Shutting down…")
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # Block main thread
    signal.pause()


if __name__ == "__main__":
    main()

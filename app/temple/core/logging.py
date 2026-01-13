from __future__ import annotations

import logging


def configure_logging() -> None:
    """Konfiguriert Logging.

    Keine „Enterprise Observability“. Nur genug Licht,
    damit wir sehen, *wo* es knackt, wenn es knackt.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

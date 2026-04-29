"""
Demo mode service for instant tip processing.

When demo mode is enabled:
- The PC is woken via WoL immediately (so it's warm for requests)
- Each new tip triggers background processing + promotion
  instead of waiting for the 2 AM nightly job
"""
import logging
import threading
from backend.utils.wol import get_wol

logger = logging.getLogger(__name__)

_demo_mode = False
_lock = threading.Lock()


def is_demo_mode() -> bool:
    return _demo_mode


def enable_demo_mode() -> dict:
    """Enable demo mode and wake the PC."""
    global _demo_mode
    with _lock:
        _demo_mode = True

    wol = get_wol()
    pc_awake = wol.is_pc_awake()
    wol_sent = False

    if not pc_awake:
        logger.info("Demo mode enabled — waking PC")
        wol_sent = True
        pc_awake = wol.wake()
    else:
        logger.info("Demo mode enabled — PC already awake")

    return {
        "demo_mode": True,
        "pc_awake": pc_awake,
        "wol_sent": wol_sent,
    }


def disable_demo_mode() -> dict:
    global _demo_mode
    with _lock:
        _demo_mode = False
    logger.info("Demo mode disabled")
    return {"demo_mode": False}


def get_status() -> dict:
    wol = get_wol()
    return {
        "demo_mode": _demo_mode,
        "pc_awake": wol.is_pc_awake(),
    }

"""Network utilities"""
import socket
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def check_host_reachable(host: str, port: int, timeout: int = 5) -> bool:
    """Check if a host is reachable on a specific port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.debug(f"Host reachability check error: {e}")
        return False


def get_local_ip() -> Optional[str]:
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


"""Wake-on-LAN utilities"""
import logging
import socket
import struct
import time
import subprocess
from typing import Optional
from wakeonlan import send_magic_packet
from backend.config import settings

logger = logging.getLogger(__name__)


class WakeOnLAN:
    """Wake-on-LAN utility"""
    
    def __init__(self, mac_address: str, ip_address: Optional[str] = None, port: int = 9):
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.port = port
    
    def is_pc_awake(self, timeout: int = 2) -> bool:
        """Check if PC is awake by attempting to connect"""
        if not self.ip_address:
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.ip_address, 22))  # Try SSH port
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"PC wake check error: {e}")
            return False
    
    def wake(self, retries: int = 3, retry_delay: int = 5) -> bool:
        """Send wake-on-LAN magic packet"""
        if not self.mac_address:
            logger.error("MAC address not configured")
            return False
        
        # Check if already awake
        if self.is_pc_awake():
            logger.info("PC is already awake")
            return True
        
        for attempt in range(retries):
            try:
                logger.info(f"Attempting to wake PC (attempt {attempt + 1}/{retries})")
                send_magic_packet(self.mac_address, ip_address=self.ip_address, port=self.port)
                
                # Wait a bit for PC to start
                time.sleep(10)
                
                # Check if PC is now awake
                if self.is_pc_awake(timeout=30):
                    logger.info("PC successfully awakened")
                    return True
                else:
                    logger.warning(f"Wake packet sent but PC not responding (attempt {attempt + 1})")
                    if attempt < retries - 1:
                        time.sleep(retry_delay)
            
            except Exception as e:
                logger.error(f"Wake-on-LAN error (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(retry_delay)
        
        logger.error("Failed to wake PC after all retries")
        return False
    
    def sleep_pc(self) -> bool:
        """Put PC to sleep (requires SSH access)"""
        if not self.ip_address:
            logger.error("IP address not configured for sleep command")
            return False
        
        try:
            # Use SSH to execute sleep command (Linux/Mac)
            # This requires SSH key authentication to be set up
            result = subprocess.run(
                ["ssh", f"user@{self.ip_address}", "systemctl suspend"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to put PC to sleep: {e}")
            return False


def get_wol() -> WakeOnLAN:
    """Get Wake-on-LAN instance from settings"""
    return WakeOnLAN(
        mac_address=settings.pc_mac_address,
        ip_address=settings.pc_ip_address,
        port=settings.pc_port
    )


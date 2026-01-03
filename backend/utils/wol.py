"""Wake-on-LAN utilities for waking PC to perform processing tasks"""
import logging
import socket
import time
import subprocess
from typing import Optional
from wakeonlan import send_magic_packet
from backend.config import settings

logger = logging.getLogger(__name__)


class WakeOnLAN:
    """
    Wake-on-LAN utility for managing PC wake/sleep state.
    
    This class handles:
    - Checking if PC is already awake (avoids unnecessary wake packets)
    - Sending WOL magic packets to wake sleeping PC
    - Putting PC to sleep after processing (optional)
    
    Network path: Raspberry Pi (ethernet) -> Router -> WiFi -> Node -> PC
    WOL packets are sent via UDP port 9 to the PC's MAC address.
    """
    
    def __init__(self, mac_address: str, ip_address: Optional[str] = None, port: int = 9):
        """
        Initialize WOL utility.
        
        Args:
            mac_address: MAC address of PC's network adapter
            ip_address: IP address of PC (for checking if awake)
            port: UDP port for WOL packets (default: 9)
        """
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.port = port
    
    def is_pc_awake(self, timeout: int = 2) -> bool:
        """
        Check if PC is already awake by attempting to connect.
        
        This prevents sending unnecessary wake packets if PC is already on.
        Tests connectivity to PC's SSH port (22) as an indicator.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if PC is reachable, False otherwise
        """
        if not self.ip_address:
            return False
        
        try:
            # Try to connect to SSH port (22) to check if PC is awake
            # This is a lightweight check - doesn't require authentication
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.ip_address, 22))  # Try SSH port
            sock.close()
            return result == 0  # 0 means connection successful
        except Exception as e:
            logger.debug(f"PC wake check error: {e}")
            return False
    
    def wake(self, retries: int = 3, retry_delay: int = 5) -> bool:
        """
        Send wake-on-LAN magic packet to wake PC.
        
        If PC is already awake, returns True immediately without sending packet.
        Otherwise sends WOL magic packet via UDP port 9 to PC's MAC address.
        The packet travels: Pi -> Router -> WiFi -> Node -> PC network adapter.
        
        Args:
            retries: Number of retry attempts if wake fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            True if PC is awake (either already was or successfully woken), False otherwise
        """
        if not self.mac_address:
            logger.error("MAC address not configured")
            return False
        
        # Check if already awake - if so, no need to send wake packet
        if self.is_pc_awake():
            logger.info("PC is already awake - skipping wake packet")
            return True
        
        # PC is sleeping - send wake packet
        for attempt in range(retries):
            try:
                logger.info(f"Attempting to wake PC (attempt {attempt + 1}/{retries})")
                
                # Send WOL magic packet: UDP broadcast to MAC address
                # Packet contains PC's MAC address repeated 16 times
                # Network adapter recognizes this pattern and wakes the PC
                send_magic_packet(self.mac_address, ip_address=self.ip_address, port=self.port)
                
                # Wait for PC to boot up (network adapter wakes, OS boots, services start)
                # This can take 10-30 seconds depending on PC speed
                time.sleep(10)
                
                # Verify PC is now awake and reachable
                if self.is_pc_awake(timeout=30):
                    logger.info("PC successfully awakened and is now reachable")
                    return True
                else:
                    logger.warning(f"Wake packet sent but PC not responding yet (attempt {attempt + 1})")
                    if attempt < retries - 1:
                        time.sleep(retry_delay)
            
            except Exception as e:
                logger.error(f"Wake-on-LAN error (attempt {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(retry_delay)
        
        logger.error("Failed to wake PC after all retries")
        return False
    
    def sleep_pc(self) -> bool:
        """
        Put PC to sleep after processing is complete (optional).
        
        Uses SSH to execute sleep command on PC. Requires:
        - SSH key authentication set up (passwordless login)
        - PC running Linux/Mac (systemctl suspend)
        - PC accessible via SSH
        
        Note: This is optional - PC can stay awake if desired.
        
        Returns:
            True if sleep command succeeded, False otherwise
        """
        if not self.ip_address:
            logger.error("IP address not configured for sleep command")
            return False
        
        try:
            # Use SSH to execute sleep command on PC
            # This requires SSH key authentication to be set up
            # Command: systemctl suspend (Linux) or pmset sleepnow (Mac)
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

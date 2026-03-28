import socket
from typing import Optional, List

class TargetResolver:
    """Target resolution and validation for PortSight."""
    
    @staticmethod
    def resolve(target: str) -> Optional[str]:
        """
        Resolves domain names or validates IP addresses.
        Returns IP address if successful, else None.
        """
        try:
            # Check if target is IP address
            return socket.gethostbyname(target)
        except (socket.gaierror, socket.herror) as e:
            # Handle resolution errors
            print(f"[ERROR] Could not resolve host '{target}': {e}")
            return None
        except Exception as e:
            print(f"[ERROR] Unexpected error resolving host '{target}': {e}")
            return None

    @staticmethod
    def get_hostname(ip: str) -> Optional[str]:
        """Attempt reverse DNS lookup."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            return "Unknown Host"
        except Exception:
            return None

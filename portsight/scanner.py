import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from datetime import datetime

class PortScanner:
    """Core scanning logic for PortSight."""
    
    def __init__(self, target_ip: str, timeout: float = 1.0, max_threads: int = 100):
        self.target_ip = target_ip
        self.timeout = timeout
        self.max_threads = max_threads
        self.results: List[Dict] = []
        self._lock = threading.Lock()

    def scan_port(self, port: int) -> Optional[Dict]:
        """
        Attempts to connect to a specific TCP port.
        Returns a result dictionary if open, else None.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.target_ip, port))
                
                if result == 0:
                    # Port is open
                    return {
                        "port": port,
                        "status": "open",
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception:
            pass
        return None

    def scan_ports(self, ports: List[int], callback=None) -> List[Dict]:
        """
        Scans a list of ports using a thread pool.
        """
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.scan_port, port) for port in ports]
            
            for future in futures:
                result = future.result()
                if result:
                    with self._lock:
                        self.results.append(result)
                if callback:
                    callback()
                    
        return sorted(self.results, key=lambda x: x["port"])

    @staticmethod
    def compare_results(old_results: List[Dict], new_results: List[Dict]) -> List[Dict]:
        """
        Compares two sets of scan results.
        Returns a list of results with a 'change' status.
        """
        old_ports = {r["port"]: r for r in old_results}
        new_ports = {r["port"]: r for r in new_results}
        
        comparison = []
        
        # All ports in current scan
        for port, result in new_ports.items():
            if port not in old_ports:
                result["change"] = "OPENED"
            else:
                result["change"] = "PERSISTENT"
            comparison.append(result)
            
        # Ports that were open before but not now
        for port, result in old_ports.items():
            if port not in new_ports:
                result["status"] = "closed"
                result["change"] = "CLOSED"
                comparison.append(result)
                
        return sorted(comparison, key=lambda x: x["port"])

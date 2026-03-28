import argparse
from typing import List, Tuple, Optional

class CommandLineInterface:
    """Handles argument parsing for PortSight."""
    
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(
            description="[PortSight] - Professional High-Performance TCP Port Scanner",
            epilog="Example: python main.py scanme.nmap.org --ports 80,443,22 --threads 50"
        )
        
        parser.add_argument("target", help="Target IP address or domain name")
        parser.add_argument("-p", "--ports", help="Port(s) to scan. Ex: 80, 22-443, 1-1024", default="1-1024")
        parser.add_argument("-t", "--threads", type=int, help="Number of concurrent threads (default: 100)", default=100)
        parser.add_argument("-w", "--timeout", type=float, help="Socket timeout in seconds (default: 1.0)", default=1.0)
        parser.add_argument("-o", "--output", help="Output filename for results")
        parser.add_argument("-f", "--format", choices=["json", "csv"], help="Export format (json or csv)", default="json")
        parser.add_argument("--report", help="Output filename for a professional HTML report")
        parser.add_argument("--compare", help="Path to a previous JSON scan file for comparison")
        parser.add_argument("--no-banner", action="store_true", help="Disable banner grabbing")
        
        return parser.parse_args()

    @staticmethod
    def parse_ports(port_input: str) -> List[int]:
        """
        Parses port input strings (e.g., '80', '22-443', '80,443').
        Returns a sorted list of unique port integers.
        """
        ports = set()
        
        try:
            for part in port_input.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    # Safety check for range
                    start = max(1, min(65535, start))
                    end = max(1, min(65535, end))
                    if start <= end:
                        ports.update(range(start, end + 1))
                else:
                    port = int(part)
                    if 1 <= port <= 65535:
                        ports.add(port)
        except ValueError:
            print(f"[ERROR] Invalid port specification: '{port_input}'")
            return []
            
        return sorted(list(ports))

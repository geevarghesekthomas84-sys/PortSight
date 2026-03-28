import socket
from typing import Optional, Dict

class ServiceDetector:
    """Service detection and banner grabbing for PortSight."""
    
    # Common TCP Port to Service mapping (IANA)
    PORT_MAP = {
        20: "FTP-Data",
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        111: "RPCBind",
        135: "MSRPC",
        139: "NetBIOS",
        143: "IMAP",
        443: "HTTPS",
        445: "Microsoft-DS",
        993: "IMAPS",
        995: "POP3S",
        1723: "PPTP",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        8080: "HTTP-Proxy"
    }

    @staticmethod
    def get_service_name(port: int) -> str:
        """Looks up a service name by port number."""
        return ServiceDetector.PORT_MAP.get(port, socket.getservbyport(port, "tcp") if port < 1024 else "Unknown Service")

    @staticmethod
    def grab_banner(target_ip: str, port: int, timeout: float = 2.0) -> Optional[str]:
        """
        Attempts to grab a banner from an open port.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((target_ip, port))
                
                # Try simple banner grabbing
                if port in [80, 8080]:
                    # HTTP Probe
                    s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n\r\n")
                
                banner = s.recv(1024).decode(errors="ignore").strip()
                if banner:
                    return banner[:100] # Return truncated banner
        except Exception:
            pass
        return None

    @staticmethod
    def get_security_insights(open_results: List[Dict]) -> List[Dict]:
        """
        Analyzes open ports and provides security insights categorized by severity.
        """
        insights = []
        open_ports = {r["port"] for r in open_results}
        
        # Security logic based on common risky ports
        risk_map = {
            21: ("CRITICAL", "FTP (Unencrypted) exposed. Use SFTP or FTPS instead."),
            23: ("CRITICAL", "Telnet (Unencrypted) exposed. Use SSH for remote access."),
            22: ("WARNING", "SSH exposed. Ensure key-based authentication is enforced and root login is disabled."),
            80: ("INFO", "HTTP web service detected. Ensure sensitive data is moved to HTTPS (Port 443)."),
            443: ("INFO", "HTTPS web service detected. Verify SSL/TLS certificates and cipher suites."),
            445: ("CRITICAL", "SMB/Microsoft-DS exposed. Potential risk for EternalBlue or similar exploits. Filter this port."),
            3389: ("CRITICAL", "RDP (Remote Desktop) exposed. High risk for brute-force attacks. Use a VPN instead."),
            3306: ("WARNING", "MySQL database exposed. Ensure strong passwords and restrict access to known IPs."),
            5432: ("WARNING", "PostgreSQL database exposed. Restrict access and ensure robust authentication."),
            8080: ("INFO", "HTTP Proxy/Alternative web port detected. Review for exposed admin interfaces.")
        }

        for port, (severity, message) in risk_map.items():
            if port in open_ports:
                insights.append({
                    "port": port,
                    "severity": severity,
                    "message": message
                })

        return sorted(insights, key=lambda x: ["CRITICAL", "WARNING", "INFO"].index(x["severity"]))

import pytest
from portsight.scanner import PortScanner
from portsight.cli import CommandLineInterface as CLI
from portsight.resolver import TargetResolver
from portsight.services import ServiceDetector

def test_port_parsing_single():
    assert CLI.parse_ports("80") == [80]

def test_port_parsing_multiple():
    assert CLI.parse_ports("80,443,22") == [22, 80, 443]

def test_port_parsing_range():
    assert CLI.parse_ports("20-25") == [20, 21, 22, 23, 24, 25]

def test_port_parsing_complex():
    assert CLI.parse_ports("80, 443, 20-22") == [20, 21, 22, 80, 443]

def test_port_parsing_invalid():
    assert CLI.parse_ports("abc") == []

def test_resolver_validation():
    assert TargetResolver.resolve("127.0.0.1") == "127.0.0.1"

def test_service_lookup():
    assert ServiceDetector.get_service_name(80) == "HTTP"
    assert ServiceDetector.get_service_name(22) == "SSH"
    assert ServiceDetector.get_service_name(443) == "HTTPS"

def test_comparison_logic():
    old = [{"port": 80, "status": "open"}]
    new = [{"port": 80, "status": "open"}, {"port": 443, "status": "open"}]
    
    comp = PortScanner.compare_results(old, new)
    
    p80 = next(r for r in comp if r["port"] == 80)
    assert p80["change"] == "PERSISTENT"
    
    p443 = next(r for r in comp if r["port"] == 443)
    assert p443["change"] == "OPENED"

def test_comparison_logic_closed():
    old = [{"port": 22, "status": "open"}]
    new = []
    
    comp = PortScanner.compare_results(old, new)
    
    p22 = next(r for r in comp if r["port"] == 22)
    assert p22["change"] == "CLOSED"
    assert p22["status"] == "closed"

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text
from typing import List, Dict, Any

class PortSightOutput:
    """Rich-based CLI output formatting for PortSight."""
    
    def __init__(self):
        self.console = Console()

    def print_banner(self):
        """Displays the startup branding banner."""
        ascii_logo = """
    ____                 __  _____ _       __    __ 
   / __ \____  _________/ /_/ ___/(_)___ _/ /_  / /_
  / /_/ / __ \/ ___/ __  / /\__ \/ / __ `/ __ \/ __/
 / ____/ /_/ / /  / /_/ / /___/ / / /_/ / / / / /_  
/_/    \____/_/   \__,_/_//____/_/\__, /_/ /_/\__/  
                                 /____/             
        """
        self.console.print(Panel(Text(ascii_logo, style="bold cyan"), subtitle="[bold blue]v1.0.0[/bold blue]", border_style="blue", expand=False))

    def print_target_info(self, target: str, ip: str, hostname: str):
        """Display info about the current scan target."""
        self.console.print(f"[bold blue][INFO][/bold blue] Target: [cyan]{target}[/cyan]")
        self.console.print(f"[bold blue][INFO][/bold blue] Resolved Address: [cyan]{ip}[/cyan]")
        self.console.print(f"[bold blue][INFO][/bold blue] Hostname: [cyan]{hostname}[/cyan]")
        self.console.print("")

    def create_progress_bar(self, total: int):
        """Creates a stylized progress bar."""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        )
        return progress

    def print_results_table(self, results: List[Dict]):
        """Renders the scan results in a clean table format."""
        if not results:
            self.console.print("\n[yellow][WARN] No open ports found.[/yellow]")
            return

        table = Table(title="\nScan Results", title_justify="center", border_style="dim")
        table.add_column("PORT", style="bold green", justify="right")
        table.add_column("STATUS", style="bold cyan", justify="center")
        table.add_column("SERVICE", style="yellow")
        table.add_column("BANNER/IDENTIFICATION", style="italic")
        table.add_column("TIMESTAMP", style="dim cyan")

        for r in results:
            table.add_row(
                str(r["port"]),
                "OPEN",
                r.get("service", "Unknown"),
                r.get("banner", "None"),
                r.get("timestamp", "").split("T")[-1].split(".")[0] # Short time
            )

        self.console.print(table)

    def print_comparison_table(self, results: List[Dict]):
        """Renders the comparison results in a clean table format."""
        if not results:
            self.console.print("\n[yellow][WARN] No comparison data available.[/yellow]")
            return

        table = Table(title="\nScan Comparison", title_justify="center", border_style="dim")
        table.add_column("PORT", style="bold green", justify="right")
        table.add_column("STATUS", style="bold cyan", justify="center")
        table.add_column("CHANGE", style="bold")
        table.add_column("SERVICE", style="yellow")
        table.add_column("BANNER/IDENTIFICATION", style="italic")

        for r in results:
            change = r.get("change", "PERSISTENT")
            change_style = "bold green" if change == "OPENED" else "bold red" if change == "CLOSED" else "cyan"
            
            table.add_row(
                str(r["port"]),
                r["status"].upper(),
                f"[{change_style}]{change}[/{change_style}]",
                r.get("service", "Unknown"),
                r.get("banner", "None")
            )

        self.console.print(table)

    def print_security_insights(self, insights: List[Dict]):
        """Displays categorized security insights in the terminal."""
        if not insights:
            return

        self.console.print("\n")
        self.console.rule("[bold cyan]SECURITY INSIGHTS[/bold cyan]")
        for insight in insights:
            port = insight["port"]
            severity = insight["severity"]
            message = insight["message"]

            if severity == "CRITICAL":
                color = "bold red"
                label = "!!"
            elif severity == "WARNING":
                color = "bold yellow"
                label = "!"
            else:
                color = "bold blue"
                label = "i"

            self.console.print(f"[{color}]{label} {severity:<8}[/{color}] | [cyan]Port {port:<5}[/cyan] | {message}")
        
        self.console.print("\n")

    def print_summary(self, total_ports: int, open_ports: int, duration: float):
        """Prints a final summary of the scan."""
        summary = Text("\nSCAN SUMMARY\n", style="bold cyan")
        summary.append(f"Total scanned: {total_ports}\n")
        summary.append(f"Open ports found: {open_ports}\n")
        summary.append(f"Scan duration: {duration:.2f} seconds\n")
        self.console.print(Panel(summary, style="blue", expand=False))

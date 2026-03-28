import sys
import time
from typing import List, Dict
from portsight.scanner import PortScanner
from portsight.resolver import TargetResolver
from portsight.services import ServiceDetector
from portsight.output import PortSightOutput
from portsight.cli import CommandLineInterface as CLI
from portsight.exporter import ResultExporter

def main():
    # 1. Initialize professional output
    output = PortSightOutput()
    output.print_banner()

    # 2. Parse command line arguments
    args = CLI.parse_args()
    
    # 3. Handle target resolution
    target_ip = TargetResolver.resolve(args.target)
    if not target_ip:
        sys.exit(1)
        
    hostname = TargetResolver.get_hostname(target_ip)
    output.print_target_info(args.target, target_ip, hostname)

    # 4. Parse port ranges
    ports_to_scan = CLI.parse_ports(args.ports)
    if not ports_to_scan:
        sys.exit(1)

    # 5. Initialize scanner
    scanner = PortScanner(target_ip, timeout=args.timeout, max_threads=args.threads)
    
    # 6. Execute Scan with progress bar
    start_time = time.time()
    
    with output.create_progress_bar(len(ports_to_scan)) as progress:
        task = progress.add_task(f"[cyan]Scanning {len(ports_to_scan)} ports...", total=len(ports_to_scan))
        
        # Define callback for progress updates
        def update_progress():
            progress.update(task, advance=1)
            
        open_results = scanner.scan_ports(ports_to_scan, callback=update_progress)

    # 7. Perform Service Detection on open ports
    if not args.no_banner:
        progress = output.console.status("[bold yellow]Detecting services and grabbing banners...", spinner="bouncingBar")
        with progress:
            for result in open_results:
                port = result["port"]
                result["service"] = ServiceDetector.get_service_name(port)
                result["banner"] = ServiceDetector.grab_banner(target_ip, port)
                
    # 8. Render Results
    duration = time.time() - start_time
    
    if args.compare:
        old_results = ResultExporter.load_results(args.compare)
        if old_results:
            comparison_results = PortScanner.compare_results(old_results, open_results)
            output.print_comparison_table(comparison_results)
        else:
            output.console.print("\n[bold red][ERROR][/bold red] Skipping comparison due to invalid history file.")
            output.print_results_table(open_results)
    else:
        output.print_results_table(open_results)
        
    output.print_summary(len(ports_to_scan), len(open_results), duration)

    # 9. Handle Exporting
    if args.output:
        if args.format == "json":
            ResultExporter.export_json(open_results, args.output, args.target)
        elif args.format == "csv":
            ResultExporter.export_csv(open_results, args.output, args.target)

    # 7. Security Insights
    insights = ServiceDetector.get_security_insights(open_results)
    output.print_security_insights(insights)

    # 8. Comparison Summary
    if args.report:
        # Pass comparison_results if comparison was performed
        comp_res = comparison_results if args.compare and 'comparison_results' in locals() else None
        ResultExporter.export_html(open_results, args.report, args.target, comparison_results=comp_res)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Scan interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[FATAL ERROR] An unexpected error occurred: {e}")
        sys.exit(1)

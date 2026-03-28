import json
import csv
from typing import List, Dict
from datetime import datetime

class ResultExporter:
    """Exports scan results to JSON or CSV formats."""
    
    @staticmethod
    def export_json(results: List[Dict], filename: str, target: str):
        """Standard JSON export including metadata."""
        data = {
            "target": target,
            "scan_timestamp": datetime.now().isoformat(),
            "results": results
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"[SUCCESS] Exported results to JSON: '{filename}'")

    @staticmethod
    def export_csv(results: List[Dict], filename: str, target: str):
        """Standard CSV export."""
        fieldnames = ["port", "status", "timestamp", "service", "banner"]
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                # Ensure all fields exist
                row = {k: r.get(k, "") for k in fieldnames}
                writer.writerow(row)
        print(f"[SUCCESS] Exported results to CSV: '{filename}'")

    @staticmethod
    def load_results(filename: str) -> List[Dict]:
        """Loads results from a previous JSON export for comparison."""
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                return data.get("results", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ERROR] Could not load comparison file '{filename}': {e}")
            return []

    @staticmethod
    def export_html(results: List[Dict], filename: str, target: str, comparison_results: List[Dict] = None):
        """Generates a professional Enterprise Light HTML report."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine which results to show in the table
        display_results = comparison_results if comparison_results else results
        is_comparison = comparison_results is not None
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PortSight Scan Report - {target}</title>
    <style>
        :root {{
            --primary: #2563eb;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
            --text-light: #64748b;
            --border: #e2e8f0;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.5;
            margin: 0;
            padding: 2rem;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 2rem;
        }}
        h1 {{
            margin: 0;
            color: var(--primary);
            font-size: 2rem;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        .badge-primary {{ background: #dbeafe; color: var(--primary); }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }}
        .stat-label {{ color: var(--text-light); font-size: 0.875rem; }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        th {{
            text-align: left;
            padding: 1rem;
            border-bottom: 2px solid var(--border);
            color: var(--text-light);
            font-weight: 600;
        }}
        td {{
            padding: 1rem;
            border-bottom: 1px solid var(--border);
        }}
        .status-open {{ color: var(--success); font-weight: 600; }}
        .status-closed {{ color: var(--danger); font-weight: 600; }}
        .change-tag {{
            font-size: 0.75rem;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .tag-opened {{ background: #dcfce7; color: var(--success); }}
        .tag-closed {{ background: #fee2e2; color: var(--danger); }}
        .tag-persistent {{ background: #f1f5f9; color: var(--text-light); }}
        footer {{
            text-align: center;
            color: var(--text-light);
            font-size: 0.875rem;
            margin-top: 3rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge badge-primary">v1.0.0 Report</div>
            <h1>PortSight Scan Report</h1>
            <p style="color: var(--text-light)">Generated on {now} for target: <strong>{target}</strong></p>
        </header>

        <div class="card grid">
            <div>
                <div class="stat-label">Total Ports Scanned</div>
                <div class="stat-value">{len(results)}</div>
            </div>
            <div>
                <div class="stat-label">Open Ports Found</div>
                <div class="stat-value" style="color: var(--success)">{len([r for r in display_results if r['status'] == 'open'])}</div>
            </div>
            <div>
                <div class="stat-label">Scan Mode</div>
                <div class="stat-value">{'Comparison' if is_comparison else 'Standard'}</div>
            </div>
        </div>

        <div class="card">
            <h2 style="margin-top:0">Scan Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Port</th>
                        <th>Status</th>
                        { '<th>Change</th>' if is_comparison else '' }
                        <th>Service</th>
                        <th>Identification</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for r in display_results:
            status_class = "status-open" if r["status"] == "open" else "status-closed"
            change_html = ""
            if is_comparison:
                change = r.get("change", "PERSISTENT")
                tag_class = f"tag-{change.lower()}"
                change_html = f'<td><span class="change-tag {tag_class}">{change}</span></td>'
                
            html_template += f"""
                    <tr>
                        <td><strong>{r['port']}</strong></td>
                        <td class="{status_class}">{r['status'].upper()}</td>
                        {change_html}
                        <td>{r.get('service', 'Unknown')}</td>
                        <td style="font-family: monospace; font-size: 0.875rem;">{r.get('banner', 'None')}</td>
                    </tr>
            """
            
        html_template += """
                </tbody>
            </table>
        </div>

        <footer>
            Built with PortSight - Professional Multi-threaded Port Scanner.
        </footer>
    </div>
</body>
</html>
        """
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_template)
        print(f"[SUCCESS] Exported results to HTML: '{filename}'")

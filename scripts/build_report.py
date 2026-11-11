"""Render a real Semgrep JSON result and record exactly which sources it describes."""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    raw_path = REPORTS / "semgrep.json"
    data = json.loads(raw_path.read_text())
    if data.get("errors"):
        raise SystemExit("Scanner reported errors; resolve them before publishing a candidate report.")
    findings = sorted(data.get("results", []), key=lambda r: (r["path"], r["start"]["line"], r["check_id"]))
    scanned_paths = data.get("paths", {}).get("scanned", [])
    source_paths = sorted({path for path in (ROOT / "helpdesk").rglob("*")
                           if path.is_file() and "__pycache__" not in path.parts}
                          | {ROOT / name for name in ("requirements.txt", "requirements-scan.txt", "Dockerfile", "compose.yaml", "scan-rules/training.yml")})
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scanner": "Semgrep Community Edition",
        "scanner_version": data.get("version"),
        "command": "semgrep scan --config scan-rules/training.yml --metrics=off --disable-version-check --json --output reports/semgrep.json helpdesk",
        "rule_policy": "Local educational rules; not a production audit or an exhaustive scan.",
        "finding_count": len(findings),
        "scanned_paths": scanned_paths,
        "semgrep_json_sha256": digest(raw_path),
        "source_sha256": {str(path.relative_to(ROOT)): digest(path) for path in source_paths},
    }
    (REPORTS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    intro = (f"Actual Semgrep {data.get('version')} scan using local educational rules. "
             f"{len(findings)} findings across {len(scanned_paths)} scanned Python files. "
             "Scanner priority is an initial triage label, not a verified impact assessment. "
             "Some alerts may not be exploitable; other issues may be absent from this report.")
    md = ["# HelpSpace — scanner findings", "", intro, "", "See `manifest.json` for the exact command and source hashes.", ""]
    cards = []
    for number, result in enumerate(findings, 1):
        finding_id = f"HS-{number:02}"
        path = result["path"]
        source = (ROOT / path).resolve()
        if not source.is_relative_to(ROOT):
            raise SystemExit("Scanner returned a source path outside the repository")
        line = result["start"]["line"]
        end = result["end"]["line"]
        code_lines = source.read_text().splitlines()
        snippet = "\n".join(f"{n + 1:>4}  {code_lines[n]}".rstrip() for n in range(max(0, line-3), min(len(code_lines), end+2)))
        extra = result["extra"]
        priority = extra.get("metadata", {}).get("triage_priority", extra["severity"])
        rule = result["check_id"]
        message = extra["message"]
        md += [f"## {finding_id} — {rule}", "", f"**Scanner priority:** {priority} · **Location:** `{path}:{line}`", "", message, "", "```text", snippet, "```", ""]
        cards.append(f'<article><h2>{finding_id} · {html.escape(rule)}</h2><p><strong>Scanner priority: {html.escape(priority)}</strong> · <code>{html.escape(path)}:{line}</code></p><p>{html.escape(message)}</p><pre>{html.escape(snippet)}</pre></article>')
    (REPORTS / "scan-report.md").write_text("\n".join(md))
    document = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>HelpSpace scanner findings</title><style>body{font:16px/1.6 system-ui,sans-serif;color:#18283d;background:#f3f5f8;max-width:1040px;margin:40px auto;padding:0 24px}header,article{background:white;padding:24px;border:1px solid #cdd7e2;border-radius:10px;margin-bottom:20px}h1{margin-top:0}h2{font-size:19px}pre{background:#edf2f7;padding:16px;overflow:auto;font-size:13px}code{font-size:14px}</style></head><body>'''
    document += f'<header><h1>HelpSpace — scanner findings</h1><p>{html.escape(intro)}</p><p>Consult manifest.json for the source hashes and exact scan command. Use the candidate submission template to record your conclusions.</p></header>'
    document += "".join(cards) + "</body></html>\n"
    (REPORTS / "scan-report.html").write_text(document)
    print(f"Rendered {len(findings)} findings; source hashes recorded in reports/manifest.json")


if __name__ == "__main__":
    main()

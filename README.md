# HelpSpace — junior application security exercise

HelpSpace is a small Python/Flask support-ticket application. Your task is to assess
security findings, investigate the code and explain practical improvements.
Read [the candidate brief](docs/CANDIDATE_BRIEF.md) before starting.

**This application deliberately contains security weaknesses. Run it only on your
own machine with the fictional data provided. Do not expose it publicly or connect
it to real accounts, documents, services, or company systems.**

## Start with Docker

Requirements: Docker Engine/Desktop with Compose v2; port 8080 available.

```bash
docker compose up --build
```

Open <http://127.0.0.1:8080>. The first build downloads dependencies; later starts
reuse them. The published port binds only to localhost. The lab network does not
provide outbound access to the running application. No API key is required.

Stop with `Ctrl+C` or `docker compose down`. To reset **this exercise's data**, run
`docker compose down -v`, then start again. This deletes the lab's database and
comments, not your source edits.

## Start without Docker

Use Python 3.11 or 3.12:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m helpdesk
```

On Windows activate with `.venv\Scripts\Activate.ps1`. Open the same localhost
URL. The SQLite database, generated session key and attachments live under
`instance/`. With the server stopped, remove that directory to reset local data.
Use an isolated environment; no system-wide installation is required.

## Fictional accounts

All three accounts use the lab-only password **`ReviewLab-2026!`**.

| Email | Organization | Role |
|---|---|---|
| alice@northstar.example | Northstar Studio | Member |
| maria@northstar.example | Northstar Studio | Administrator |
| bob@harbor.example | Harbor Labs | Member |

Use separate browser profiles or sign out when switching users. These credentials
and predictable fixture IDs are intentionally supplied for testing, not findings.

## Your materials

- [Candidate brief and intended permissions](docs/CANDIDATE_BRIEF.md)
- [Readable scanner report](reports/scan-report.md), also available as
  [standalone HTML](reports/scan-report.html)
- [Original Semgrep JSON](reports/semgrep.json) and [scan provenance](reports/manifest.json)
- [Submission template](docs/SUBMISSION_TEMPLATE.md)
- Application code in `helpdesk/`; deployment settings in `compose.yaml` and `Dockerfile`

The report is an **actual Semgrep run using local educational rules**. It is not a
claim that the built-in production Semgrep rules detect all these issues. Rules
are intentionally broad to create a triage exercise. A finding is not proof; the
report is not exhaustive. No AI-generated conclusions are supplied as facts.

## Optional tools and checks

You may use AI assistants, scanners, a browser, curl, or your editor. No paid tool
is required. If the employer expects a particular paid tool, they will provide
equivalent access. See the brief for what to record about tool use.

Basic functionality checks:

```bash
python -m unittest discover -s tests -v
```

These are smoke tests, not a complete security test suite or an answer key.
To reproduce the scanner report, install the separately pinned scanner dependencies
in an isolated environment (the app does not need them):

```bash
python -m pip install -r requirements-scan.txt
semgrep scan --config scan-rules/training.yml --metrics=off --disable-version-check --json --output reports/semgrep.json helpdesk
python scripts/build_report.py
```

The report manifest identifies the scanned source by SHA-256 rather than a commit
ID, so it works before the repository's first commit. Source changes make the old
report a historical snapshot; regenerate it if you want a new scan.

## Runtime context

Default local launch: `HELPSPACE_HOST=127.0.0.1`, `HELPSPACE_DEBUG=0`.
Compose uses `0.0.0.0` inside the container and a localhost-only host port; debug
is explicitly disabled. Local HTTP explains the non-Secure session cookie in
this lab. Evaluate how any concern would change under a different deployment.

Resources: [Flask documentation](https://flask.palletsprojects.com/),
[Semgrep local rules](https://semgrep.dev/docs/running-rules).

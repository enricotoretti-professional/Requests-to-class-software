# BSP AI — Learning Pathways Prototype

An independent concept prototype exploring student career pathways, HR job-market data review, and faculty teaching-material planning for Mechanical Engineering. It is not an official University of Milano-Bicocca website or service.

## What’s included

- `index.html` — student interests and career/course exploration.
- `hr-intake.html` — HR-authorized CSV intake, validation, duplicate checks, and fictional demo data.
- `course-impact.html` — teaching-material studio for reviewing syllabus topics against student and HR snapshots.
- `server.py` — optional Python API that stores HR-submitted job records in a local SQLite database.
- `MVP_PLAN.md` — product scope, safeguards, and evaluation plan.

The browser prototype uses rules and templates; it does not connect to a live AI model. Drafts and imported browser data are not automatically published. Demo snapshots are fictional.

## Run the prototype

### Browser-only pages

Open `index.html` in a browser, or on Windows run `launch-in-chrome.bat` to open it in Chrome. The API connection is not available in browser-only mode.

### Optional local API

Python 3 is required. In PowerShell, generate separate HR and admin tokens and start the server:

```powershell
$hrToken = python -c "import secrets; print(secrets.token_urlsafe(32))"
$adminToken = python -c "import secrets; print(secrets.token_urlsafe(32))"
$env:BICOCCA_ROLE_TOKENS = (@{ hr = $hrToken; admin = $adminToken } | ConvertTo-Json -Compress)
python server.py
```

Open <http://127.0.0.1:8000> and connect from the HR intake page. The default database is created at `data/job_market.sqlite3`; set `BICOCCA_DB_PATH` to choose another location. Tokens are held only in the current terminal session by these commands.

## Data and deployment warning

Use only data you are authorized to process. The API is a local prototype, not a production authentication or deployment solution. Keep it bound to localhost; do not expose it to a network or use real student/HR data without the required institutional security, privacy, and data-governance approvals. The token mechanism is not University SSO.

## Upload to the configured GitHub repository

Review the files before staging, then run:

```powershell
git add -A
git diff --cached --stat
git commit -m "Add BSP AI learning pathways prototype"
git push -u origin main
```

Check that the GitHub repository has the intended visibility before pushing.

import hmac
import json
import mimetypes
import os
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("BICOCCA_DB_PATH", ROOT / "data" / "job_market.sqlite3"))
MAX_BODY_BYTES = 5 * 1024 * 1024
MAX_RECORDS = 1000
ALLOWED_SOURCES = {
    "LinkedIn",
    "Indeed",
    "Bicocca Career Service",
    "Other approved source",
}
STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/hr-intake.html": "hr-intake.html",
    "/course-impact.html": "course-impact.html",
}


def load_role_tokens():
    raw_tokens = os.environ.get("BICOCCA_ROLE_TOKENS")
    if not raw_tokens:
        raise RuntimeError(
            "Set BICOCCA_ROLE_TOKENS to a JSON object with hr and admin tokens."
        )
    try:
        tokens = json.loads(raw_tokens)
    except json.JSONDecodeError as error:
        raise RuntimeError("BICOCCA_ROLE_TOKENS must contain valid JSON.") from error
    if not isinstance(tokens, dict) or not tokens:
        raise RuntimeError("BICOCCA_ROLE_TOKENS must be a non-empty JSON object.")

    approved = {}
    for role, token in tokens.items():
        if role not in {"hr", "admin"} or not isinstance(token, str) or len(token) < 32:
            raise RuntimeError(
                "Configure only hr/admin roles, each with a token of at least 32 characters."
            )
        approved[role] = token
    if "hr" not in approved or "admin" not in approved:
        raise RuntimeError("Configure both hr and admin role tokens.")
    if len(set(approved.values())) != len(approved):
        raise RuntimeError("Use a different token for each role.")
    return approved


ROLE_TOKENS = {}


def connect_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS job_postings (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            source_reference TEXT NOT NULL,
            role_title TEXT NOT NULL,
            employer TEXT NOT NULL,
            location TEXT NOT NULL,
            posted_date TEXT NOT NULL,
            employment_type TEXT NOT NULL,
            description TEXT NOT NULL,
            skills_json TEXT NOT NULL,
            fingerprint TEXT NOT NULL UNIQUE,
            imported_by TEXT NOT NULL,
            imported_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


@contextmanager
def database():
    connection = connect_database()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def posting_fingerprint(record):
    fields = (
        record["source"],
        record["role_title"],
        record["employer"],
        record["location"],
        record["posted_date"],
    )
    return "|".join(value.strip().casefold() for value in fields)


def validate_record(record):
    if not isinstance(record, dict):
        return "Each record must be an object."
    for field in ("source", "role_title", "employer", "description"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            return f"{field} is required."
    if record["source"] not in ALLOWED_SOURCES:
        return "source is not an approved source."
    for field in ("source_reference", "location", "posted_date", "employment_type"):
        if not isinstance(record.get(field, ""), str):
            return f"{field} must be text."
    posted_date = record.get("posted_date", "")
    if posted_date:
        try:
            if datetime.strptime(posted_date, "%Y-%m-%d").date().isoformat() != posted_date:
                return "posted_date must be a valid YYYY-MM-DD date."
        except ValueError:
            return "posted_date must be a valid YYYY-MM-DD date."
    skills = record.get("skills")
    if (
        not isinstance(skills, list)
        or not skills
        or any(not isinstance(skill, str) or not skill.strip() for skill in skills)
    ):
        return "skills must be a non-empty list of text values."
    return None


class Handler(BaseHTTPRequestHandler):
    server_version = "BicoccaJobIntake/1.0"

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")

    def send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def authenticated_role(self):
        authorization = self.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return None
        token = authorization[7:]
        for role, expected in ROLE_TOKENS.items():
            if hmac.compare_digest(token, expected):
                return role
        return None

    def read_json_body(self):
        content_length = self.headers.get("Content-Length")
        if not content_length:
            raise ValueError("Content-Length is required.")
        try:
            size = int(content_length)
        except ValueError as error:
            raise ValueError("Content-Length is invalid.") from error
        if size < 0 or size > MAX_BODY_BYTES:
            raise ValueError("Request body exceeds the 5 MB limit.")
        try:
            return json.loads(self.rfile.read(size))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError("Request body must be valid JSON.") from error

    def do_GET(self):
        request_path = unquote(urlsplit(self.path).path)
        if request_path.startswith("/api/"):
            role = self.authenticated_role()
            if role is None:
                self.send_json(401, {"error": "Valid role token required."})
                return
            if request_path == "/api/session":
                self.send_json(200, {"role": role})
                return
            if request_path == "/api/hr/postings":
                if role not in {"hr", "admin"}:
                    self.send_json(403, {"error": "Role cannot read job postings."})
                    return
                with database() as connection:
                    rows = connection.execute(
                        """
                        SELECT id, source, source_reference, role_title, employer,
                               location, posted_date, employment_type, description,
                               skills_json, imported_by, imported_at
                        FROM job_postings
                        ORDER BY imported_at DESC
                        LIMIT 5000
                        """
                    ).fetchall()
                postings = [
                    {
                        **dict(row),
                        "skills": json.loads(row["skills_json"]),
                    }
                    for row in rows
                ]
                for posting in postings:
                    del posting["skills_json"]
                self.send_json(200, {"count": len(postings), "records": postings})
                return
            self.send_json(404, {"error": "API route not found."})
            return

        filename = STATIC_FILES.get(request_path)
        if filename is None:
            self.send_error(404)
            return
        path = ROOT / filename
        try:
            body = path.read_bytes()
        except OSError:
            self.send_error(404)
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        request_path = unquote(urlsplit(self.path).path)
        if request_path != "/api/hr/postings":
            self.send_json(404, {"error": "API route not found."})
            return

        role = self.authenticated_role()
        if role is None:
            self.send_json(401, {"error": "Valid role token required."})
            return
        if role != "hr":
            self.send_json(403, {"error": "Only HR can import job postings."})
            return

        try:
            payload = self.read_json_body()
        except ValueError as error:
            self.send_json(400, {"error": str(error)})
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            self.send_json(400, {"error": "Request must contain a records array."})
            return
        records = payload["records"]
        if not records or len(records) > MAX_RECORDS:
            self.send_json(
                400,
                {"error": f"Provide between 1 and {MAX_RECORDS} records per batch."},
            )
            return

        errors = []
        for index, record in enumerate(records, start=1):
            error = validate_record(record)
            if error:
                errors.append({"record": index, "error": error})
        if errors:
            self.send_json(400, {"error": "One or more records are invalid.", "details": errors[:20]})
            return

        imported_at = datetime.now(timezone.utc).isoformat()
        inserted = 0
        duplicates = 0
        try:
            with database() as connection:
                for record in records:
                    try:
                        connection.execute(
                            """
                            INSERT INTO job_postings (
                                id, source, source_reference, role_title, employer,
                                location, posted_date, employment_type, description,
                                skills_json, fingerprint, imported_by, imported_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                str(uuid.uuid4()),
                                record["source"],
                                record.get("source_reference", "").strip(),
                                record["role_title"].strip(),
                                record["employer"].strip(),
                                record.get("location", "").strip(),
                                record.get("posted_date", ""),
                                record.get("employment_type", "").strip(),
                                record["description"].strip(),
                                json.dumps(
                                    list(dict.fromkeys(skill.strip() for skill in record["skills"])),
                                    ensure_ascii=False,
                                ),
                                posting_fingerprint(record),
                                role,
                                imported_at,
                            ),
                        )
                        inserted += 1
                    except sqlite3.IntegrityError:
                        duplicates += 1
        except sqlite3.Error:
            self.send_json(500, {"error": "Database write failed; no success was recorded."})
            return

        self.send_json(201, {"inserted": inserted, "duplicates": duplicates})

    def do_OPTIONS(self):
        self.send_json(405, {"error": "Cross-origin requests are not supported."})


def main():
    global ROLE_TOKENS
    try:
        ROLE_TOKENS = load_role_tokens()
        with database():
            pass
        host = os.environ.get("BICOCCA_HOST", "127.0.0.1")
        port = int(os.environ.get("BICOCCA_PORT", "8000"))
        server = ThreadingHTTPServer((host, port), Handler)
    except (OSError, sqlite3.Error, ValueError, RuntimeError) as error:
        print(f"Cannot start Bicocca job intake API: {error}", file=sys.stderr)
        return 1

    print(f"Bicocca job intake listening on http://{host}:{port}")
    print(f"Database: {DATABASE_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""A local support-task tool with durable, tenant-scoped idempotency."""
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile


class IntentConflict(ValueError):
    pass


def connect(path):
    return sqlite3.connect(path, timeout=5, isolation_level=None)


def initialize(path):
    db = connect(path)
    try:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, subject TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS operations (
                tenant TEXT NOT NULL, operation_id TEXT NOT NULL,
                payload_hash TEXT NOT NULL, response TEXT NOT NULL,
                PRIMARY KEY (tenant, operation_id)
            );
        """)
    finally:
        db.close()


def create_task(path, tenant, operation_id, subject, *, fail_at=None):
    """Trusted caller supplies authorized tenant and persisted operation ID.

    No external service calls. All durable state belongs to ONE database.
    fail_at injects an exception before or after commit, not a process crash.
    """
    if not all(isinstance(v, str) and v.strip() for v in (tenant, operation_id, subject)):
        raise ValueError("Tenant, operation ID, and subject are required")
    if fail_at not in (None, "before_commit", "after_commit"):
        raise ValueError("Unknown failure injection point")
    payload = json.dumps({"version": 1, "tool": "create_task", "subject": subject},
                         sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    db = connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute(
            "SELECT payload_hash, response FROM operations WHERE tenant=? AND operation_id=?",
            (tenant, operation_id)).fetchone()
        if previous:
            if previous[0] != digest:
                raise IntentConflict("Same operation ID used with different arguments")
            response = json.loads(previous[1])
        else:
            task_id = db.execute("INSERT INTO tasks (tenant, subject) VALUES (?, ?)",
                                 (tenant, subject)).lastrowid
            response = {"task_id": task_id, "status": "created"}
            db.execute("INSERT INTO operations VALUES (?, ?, ?, ?)",
                       (tenant, operation_id, digest, json.dumps(response, sort_keys=True)))
        if fail_at == "before_commit":
            raise ConnectionError("Injected failure before commit")
        db.execute("COMMIT")
        if fail_at == "after_commit":
            raise TimeoutError("Committed, but response was lost")
        return response
    except BaseException:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()


def counts(path):
    db = connect(path)
    try:
        return tuple(db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                     for table in ("tasks", "operations"))
    finally:
        db.close()


def demo():
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "tasks.sqlite"
        initialize(path)
        try:
            create_task(path, "acme", "request-42", "Check delivery", fail_at="after_commit")
        except TimeoutError as error:
            print(error)
        print("After timeout: tasks=%d operations=%d" % counts(path))
        print("Retry:", json.dumps(create_task(path, "acme", "request-42", "Check delivery"), sort_keys=True))
        print("After retry: tasks=%d operations=%d" % counts(path))
        try:
            create_task(path, "acme", "request-42", "Change delivery")
        except IntentConflict as error:
            print("Conflict:", error)


if __name__ == "__main__":
    demo()

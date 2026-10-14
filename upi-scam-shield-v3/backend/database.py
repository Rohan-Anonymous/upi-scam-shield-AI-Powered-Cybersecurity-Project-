"""SQLite storage: reports (unique reporter), checks (for dashboard)."""
import sqlite3, os
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), "scam_shield.db")
now = lambda: datetime.now().isoformat(timespec="seconds")

def _conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT, upi_id TEXT NOT NULL,
            reason TEXT, reporter TEXT NOT NULL, created_at TEXT NOT NULL,
            UNIQUE(upi_id, reporter))""")
        c.execute("""CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, amount REAL, created_at TEXT)""")

def add_report(upi_id, reason, reporter):
    """False agar is reporter ne ye ID pehle hi report ki hai."""
    try:
        with _conn() as c:
            c.execute("INSERT INTO reports (upi_id, reason, reporter, created_at) VALUES (?,?,?,?)",
                      (upi_id.lower().strip(), reason[:120], reporter[:60], now()))
        return True
    except sqlite3.IntegrityError:
        return False

def count_reports(upi_id):
    with _conn() as c:   # alag-alag reporters ginte hain
        return c.execute("SELECT COUNT(DISTINCT reporter) FROM reports WHERE upi_id=?",
                         (upi_id.lower().strip(),)).fetchone()[0]

def latest_reports(limit=12):
    with _conn() as c:
        rows = c.execute("SELECT id, upi_id, reason, created_at FROM reports ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]

def log_check(level, amount):
    with _conn() as c:
        c.execute("INSERT INTO checks (level, amount, created_at) VALUES (?,?,?)", (level, amount, now()))

def stats():
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM checks").fetchone()[0]
        red = c.execute("SELECT COUNT(*), COALESCE(SUM(amount),0) FROM checks WHERE level='RED'").fetchone()
        reports = c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        top = c.execute("SELECT upi_id, COUNT(DISTINCT reporter) AS n FROM reports GROUP BY upi_id ORDER BY n DESC LIMIT 5").fetchall()
    return {"total_checks": total, "red_checks": red[0], "amount_in_red": red[1],
            "total_reports": reports, "top_ids": [dict(r) for r in top]}

def seed_demo():
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    if total == 0:
        for i in range(6): add_report("sbi-kyc-update@okaxis", "Fake KYC message", f"seed{i}")
        for i in range(3): add_report("refund.help123@ybl", "Fake refund call", f"seed{i}")
        for i in range(2): add_report("lottery.winner99@paytm", "Lottery scam", f"seed{i}")

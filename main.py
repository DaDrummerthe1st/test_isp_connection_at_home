import time
import sqlite3
from datetime import datetime
import subprocess

DB_FILE = "ping_results.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL,
            rtt_ms REAL
        )
    """)
    conn.commit()
    conn.close()

def log_ping(success, rtt_ms):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO pings (timestamp, success, rtt_ms) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), int(success), rtt_ms)
    )
    conn.commit()
    conn.close()

def ping_host(host):
    try:
        # -c 1: one ping, -W 2: 2 second timeout
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        success = result.returncode == 0
        rtt_ms = None
        if success:
            # Parse RTT from output
            for line in result.stdout.splitlines():
                if "time=" in line:
                    rtt_ms = float(line.split("time=")[-1].split()[0])
                    break
        return success, rtt_ms
    except Exception:
        return False, None

def main():
    init_db()
    while True:
        success, rtt_ms = ping_host('sunet.se')
        log_ping(success, rtt_ms)
        print(f"{datetime.now().isoformat()} | Success: {success} | RTT: {rtt_ms}")
        time.sleep(30)  # not 5 minutes

if __name__ == "__main__":
    main()
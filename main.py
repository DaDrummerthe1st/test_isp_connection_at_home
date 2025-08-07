#!/usr/bin/python3
from time import sleep
import sqlite3
from datetime import datetime
import subprocess
import random
from pathlib import Path

HOMEDIR = Path.home()
DB_FILE = f"{HOMEDIR}/check_internet/test_isp_connection_at_home/ping_results.db"

respondents = [
    "ping.sunet.se",
    "aftonbladet.se",
    "ping.bahnhof.se",
    "netgear.com",
    "8.8.8.8",
    "bbc.co.uk",
    "192.0.43.10",
    "4.2.2.2"
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS pings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL,
            rtt_ms FLOAT
	        respondents TEXT NOT NULL DEFAULT unknown
        )
    """)
    conn.commit()
    conn.close()

def log_ping(success, rtt_ms, respondent):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO pings (timestamp, success, rtt_ms, respondents) VALUES (?, ?, ?, ?)",
        (datetime.now().isoformat(), int(success), rtt_ms, respondent)
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
        return success, rtt_ms, host
    except Exception:
        return False, None, host

def main():
    init_db()
    # while True:
    random_respondent = respondents[random.randint(0,len(respondents)-1)]
    success, rtt_ms, _ = ping_host(random_respondent)
    log_ping(success, rtt_ms, random_respondent)
    print(f"{datetime.now().isoformat()} | Success: {success} | RTT: {rtt_ms} | {random_respondent}")
        # if success:
        #     sleep(60)
        # else:
        #     sleep(20)

if __name__ == "__main__":
    main()

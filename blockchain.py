import hashlib
import json
import sqlite3
import time

DB = "trustfund.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def calc_hash(idx, ts, typ, amt, detail, prev):
    data = json.dumps([idx, ts, typ, float(amt), detail, prev])
    return hashlib.sha256(data.encode()).hexdigest()


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS blocks (
        idx INTEGER PRIMARY KEY,
        timestamp TEXT,
        type TEXT,
        amount REAL,
        detail TEXT,
        prev_hash TEXT,
        hash TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT)""")
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]
    conn.close()
    if count == 0:
        add_block("genesis", 0, "Genesis Block")


def add_block(typ, amount, detail):
    conn = get_db()
    last = conn.execute("SELECT * FROM blocks ORDER BY idx DESC LIMIT 1").fetchone()
    idx = last["idx"] + 1 if last else 0
    prev = last["hash"] if last else "0"
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    h = calc_hash(idx, ts, typ, amount, detail, prev)
    conn.execute("INSERT INTO blocks VALUES (?,?,?,?,?,?,?)",
                 (idx, ts, typ, float(amount), detail, prev, h))
    conn.commit()
    conn.close()
    return h


def get_chain():
    conn = get_db()
    rows = conn.execute("SELECT * FROM blocks ORDER BY idx").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def verify_chain():
    chain = get_chain()
    for i, b in enumerate(chain):
        expected = calc_hash(b["idx"], b["timestamp"], b["type"],
                             b["amount"], b["detail"], b["prev_hash"])
        if expected != b["hash"]:
            return False, b["idx"], "Block data changed"
        if i > 0 and b["prev_hash"] != chain[i - 1]["hash"]:
            return False, b["idx"], "Chain link broken"
    return True, None, "Chain is valid"


if __name__ == "__main__":
    init_db()
    receipt = add_block("donation", 500, "Test Donor")
    print("Receipt hash:", receipt)
    print("Verify:", verify_chain())
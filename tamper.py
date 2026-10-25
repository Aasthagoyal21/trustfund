import sqlite3
import sys

conn = sqlite3.connect("trustfund.db")
amount = float(sys.argv[1])
conn.execute("UPDATE blocks SET amount = ? WHERE idx = 2", (amount,))
conn.commit()
conn.close()
print("Block 2 amount changed to", amount)
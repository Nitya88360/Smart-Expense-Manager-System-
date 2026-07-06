import sqlite3

conn = sqlite3.connect("expenses.db")
cur = conn.cursor()

print("Users:")
for row in cur.execute("SELECT * FROM users"):
    print(row)

print("\nExpenses:")
for row in cur.execute("SELECT * FROM expenses"):
    print(row)

conn.close()

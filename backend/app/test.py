import sqlite3

conn = sqlite3.connect("app/jobs.db")
cursor = conn.cursor()
cursor.execute("SELECT id, title FROM job_list LIMIT 5")
rows = cursor.fetchall()
print(rows)
conn.close()

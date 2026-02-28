from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "app" / "jobs.db"
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""         
CREATE TABLE "job_list" (
  "id" TEXT,
  "site" TEXT,
  "job_url" TEXT,
  "job_url_direct" TEXT,
  "title" TEXT,
  "company" TEXT,
  "location" TEXT,
  "date_posted" TEXT,
  "job_type" TEXT,
  "is_remote" INTEGER,
  "description" TEXT,
  "company_url" TEXT,
  "company_url_direct" TEXT,
  "skills" TEXT,
  "experience_range" TEXT,
  "status" TEXT DEFAULT 'all'
);
               """)

conn.commit()
conn.close()

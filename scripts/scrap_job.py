import csv
import sqlite3
import pandas as pd
from jobspy import scrape_jobs

jobs = scrape_jobs(
    # "glassdoor", "bayt", "naukri", "bdjobs"
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term="computer science intern student",
    # google_search_term="software engineer jobs near San Francisco, CA since yesterday",
    location="Calgary",
    results_wanted=20,
    hours_old=72,
    country_indeed='canada',
    # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Found {len(jobs)} jobs")

unwanted_columns = [
    # Salary-related (often missing / inconsistent)
    "salary_source",
    "interval",
    "min_amount",
    "max_amount",
    "currency",
    # Job metadata with low immediate value
    "job_function",
    "job_level",
    "listing_type",
    "vacancy_count",
    # Company enrichment (nice-to-have later)
    "company_industry",
    "company_logo",
    "company_addresses",
    "company_num_employees",
    "company_revenue",
    "company_description",
    "company_rating",
    "company_reviews_count",
    # Contact / misc
    "emails",
    # Remote granularity (keep boolean instead)
    "work_from_home_type",
]


jobs = jobs.drop(columns=unwanted_columns, errors="ignore")
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC,
            escapechar="\\", index=False)
print(jobs.head())


conn = sqlite3.connect('../data/jobs.db')
cursor = conn.cursor()

for row in jobs.itertuples(index=False):
    cursor.execute("""
                   INSERT OR IGNORE INTO job_list (id,site,job_url,job_url_direct,title,company,location,date_posted,job_type,is_remote,description,company_url,company_url_direct,skills,experience_range)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                   """, row)
conn.commit()
conn.close()
print("Job found stored into db")

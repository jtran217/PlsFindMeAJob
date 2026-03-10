from sqlalchemy import Column, String, Integer, Text
from .database import Base


class Job(Base):
    __tablename__ = "job_list"

    id = Column(String, primary_key=True, index=True)

    site = Column(String)
    job_url = Column(String)
    job_url_direct = Column(String)

    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String, index=True)

    date_posted = Column(String)
    job_type = Column(String)

    is_remote = Column(Integer) 

    description = Column(Text)

    company_url = Column(String)
    company_url_direct = Column(String)

    skills = Column(Text)
    experience_range = Column(String)
    status = Column(String)

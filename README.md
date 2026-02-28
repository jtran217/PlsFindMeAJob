# PlsFindMeAJob

> A small, incremental project to scrape job postings, display them in a simple UI, and generate tailored resumes — without over-scoping.

## Motivation

This project is a restart of an earlier idea that became too large too quickly (ML ranking, Docker, automation all at once).  
This time, the focus is on **building something usable first**, then adding features incrementally.

The goal is to prioritize:
- Simplicity
- Clear scope
- Iterative development
- Learning through shipping

## High-Level Goals

1. Scrape job postings from selected job sites
2. Store and normalize job data
3. Display postings in a simple frontend
4. Generate resumes based on job descriptions
5. Incrementally add smarter features over time

Each goal starts with the smallest possible implementation.

## Non-Goals (For Now)

- ❌ Machine learning–based ranking
- ❌ Fully automated pipelines
- ❌ Microservices or distributed systems
- ❌ Production-scale infrastructure
- ❌ “Perfect” resume generation

These may be explored later, but only after the fundamentals are solid.

## Initial Architecture
Job Sites
↓
Scraper (Python)
↓
Storage (JSON / SQLite)
↓
Backend API
↓
Simple Frontend
↓
Resume Generator

## Roadmap

### Phase 1 — Foundation
- [X] Scrape job postings from one job site
- [X] Normalize and store job data
- [X] CLI or script-based workflow

### Phase 2 — Visibility
- [ ] Simple frontend to view job postings
  - [X] Make simple fast api backend to talk to database.
  - [X] make frontend talk to backend.
  - [X] Fix job description as it includes some markdown content. Probably use a markdown render to display this text.
  - [ ] Some sort of pagination
  - [ ] have the job description be a scrollable content.
- [ ] Basic filtering and searching

### Phase 3 — Resume Generation
- [ ] Resume templates
- [ ] Generate resumes using job descriptions + user profile
- [ ] Export to PDF or DOCX

### Phase 4 — Incremental Intelligence
- [ ] Keyword matching
- [ ] Simple heuristic-based scoring
- [ ] Resume–job relevance indicators

### Phase 5 — Nice-to-Haves
- [ ] Dockerization
- [ ] Multiple job boards
- [ ] ML-based experiments (optional)

## Why This Repo Exists

This is a **learning-first project**, not a production product.



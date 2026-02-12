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


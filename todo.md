# PlsFindMeAJob - Todo List

This file tracks the project's progress and upcoming tasks.

## Completed Tasks

### Phase 1 — Foundation
- [X] Scrape job postings from one job site
- [X] Normalize and store job data
- [X] CLI or script-based workflow

### Phase 2 — Visibility
- [X] Simple frontend to view job postings
  - [X] Make simple fast api backend to talk to database
  - [X] Make frontend talk to backend
  - [X] Fix job description as it includes some markdown content. Probably use a markdown render to display this text
  - [X] Some sort of pagination
  - [X] Scrollable job card section
  - [X] Have the job description be a scrollable content

### Phase 3 — AI-Assisted Resume Generation
- [X] Define canonical resume JSON schema
- [X] Display Profile page where user can edit 
- [X] Save button to save info to profile.JSON
  - [X] Needs to display education, have fields for linkedin link
- [X] **Remove Legacy Profile System** (March 2026)
  - [X] Removed legacy profile components (`Profile.tsx`, `ProfilePage.tsx`)
  - [X] Removed legacy profile API routes (`/api/profile`)
  - [X] Removed legacy profile data files and schemas
  - [X] Updated navigation to only show "Resume Builder" button
  - [X] Cleaned up profile migration code from resume service
  - [X] Updated generate endpoint to use enhanced resume format
  - [X] Verified enhanced resume builder (`/resume`) still works fully

### Job Status Filtering System
- [X] **Fixed Job Status Tab Functionality** (March 2026)
  - [X] Restored accidentally deleted job status tabs (Ready, Applied, All Jobs)
  - [X] Implemented server-side filtering by job status
  - [X] Added job count API endpoint (`/api/jobs/count/status`)
  - [X] Updated frontend to use server-side filtering instead of client-side
  - [X] Reset all jobs to "All Jobs" status (proper workflow)

## Current Tasks

### Phase 3 — AI-Assisted Resume Generation (Continued)
- [ ] Fix date validation in resume forms (currently can type any char and date)
- [ ] Send (profile + job description) to Claude
- [ ] Receive structured JSON resume
- [ ] Inject JSON into Reactive Resume
- [ ] Export to PDF

### Phase 2 — Visibility (Remaining)
- [ ] Basic filtering and searching (beyond status filtering)

## Upcoming Tasks

### Phase 4 — Incremental Intelligence
- [ ] Keyword matching
- [ ] Simple heuristic-based scoring
- [ ] Resume–job relevance indicators

### Phase 5 — Nice-to-Haves
- [ ] Dockerization
- [ ] Multiple job boards
- [ ] ML-based experiments (optional)

## Current Priority

Focus is on completing Phase 3 — AI-Assisted Resume Generation, specifically:
1. **Date validation fixes** in the enhanced resume builder
2. **Claude integration** for resume optimization
3. **PDF export functionality**

## Notes

- **Legacy Profile System**: Completely removed in favor of enhanced resume builder
- **Job Status Workflow**: Jobs start in "All Jobs" → move to "Ready" after resume generation → move to "Applied" after submission
- **Enhanced Resume Builder**: Located at `/resume` route with comprehensive resume management features
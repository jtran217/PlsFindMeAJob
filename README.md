# PlsFindMeAJob

> Scrape job postings, build a tailored resume, and generate a PDF — all from a single dashboard.
> Designed to be self-hosted: spin it up locally with Docker and keep your data on your own machine.

## What It Does

- **Scrapes** job postings automatically on a configurable schedule (powered by [JobSpy](https://github.com/Bunsly/JobSpy))
- **Displays** jobs in a clean dashboard with filtering and markdown-rendered descriptions
- **Optimizes** your resume for a specific job using AI (OpenRouter / Claude 3.5 Haiku)
- **Generates** a polished PDF resume from a LaTeX template (Jake Resume style)

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, APScheduler |
| Database | SQLite (swappable via `DATABASE_URL`) |
| AI | OpenRouter (Claude 3.5 Haiku by default) |
| PDF | LaTeX / pdflatex |
| Deployment | Docker + Docker Compose |

## Quickstart

### Option A — Docker (recommended)

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd PlsFindMeAJob

# 2. Set up environment
cp .env.example .env
# Edit .env and fill in OPENROUTER_API_KEY

# 3. Start everything
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:6767 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### Option B — Local Development

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirement.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (separate terminal)
```bash
cd frontend
npm install
npm run dev                    # Dev server at http://localhost:5173
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | Yes | API key for AI resume optimization |
| `OPENROUTER_MODEL` | No | Defaults to `anthropic/claude-3.5-haiku` |
| `OPENROUTER_BASE_URL` | No | Defaults to `https://openrouter.ai/api/v1` |
| `OPENROUTER_MAX_TOKENS` | No | Defaults to `4096` |
| `OPENROUTER_TIMEOUT` | No | Defaults to `30` seconds |
| `DATABASE_URL` | No | Defaults to local SQLite; Docker sets this automatically |
| `ALLOWED_ORIGINS` | No | CORS origins, defaults to localhost dev ports |

## Features

### Job Dashboard
- Automatic or on-demand job scraping with configurable intervals
- Filter jobs by status: **Ready**, **Applied**, **All**
- Markdown-rendered job descriptions with syntax highlighting
- Mark jobs as applied, delete stale postings
- Auto-cleanup of jobs older than 60 days

### Resume Builder
- Structured editor for personal info, education, skills, experience, and projects
- Per-job resume versioning — your master resume stays untouched
- Load sample data to get started quickly

### AI Resume Optimization
1. Select a job from the dashboard
2. Choose which experiences and projects to include
3. Hit **Optimize** — AI rewrites bullet points to match the job's keywords
4. Review and edit the output
5. Generate and download a PDF

### PDF Generation
- LaTeX-based rendering (Jake Resume template)
- One-shot pipeline: analyze → optimize → generate in a single click
- Manual generation with reviewed content
- PDFs stored per job for later download

## Roadmap

### Phase 1 — Foundation ✅
- [x] Scrape job postings
- [x] Normalize and store job data
- [x] CLI / script-based workflow

### Phase 2 — Visibility ✅
- [x] FastAPI backend
- [x] React frontend talking to backend
- [x] Markdown rendering for job descriptions
- [x] Scrollable job list and description panel
- [ ] Pagination UI
- [ ] Filtering and search

### Phase 3 — Resume Generation ✅
- [x] Resume builder with structured sections
- [x] AI-powered bullet point optimization
- [x] PDF export via LaTeX

### Phase 4 — Incremental Intelligence 🔄
- [ ] Keyword matching and scoring UI
- [ ] Heuristic-based job relevance score
- [ ] Resume–job fit indicators

### Phase 5 — Nice-to-Haves
- [x] Dockerization
- [ ] Multiple job boards
- [ ] ML-based ranking experiments

## Project Structure

```
PlsFindMeAJob/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── database.py             # SQLAlchemy setup
│   │   ├── job_models.py           # ORM models
│   │   ├── models/                 # Pydantic schemas
│   │   └── services/               # Business logic
│   │       ├── scraper_service.py
│   │       ├── resume_service.py
│   │       ├── optimization_service.py
│   │       └── pdf_service.py
│   ├── templates/                  # LaTeX resume template
│   ├── scripts/                    # DB init, standalone scraper
│   └── requirement.txt
├── frontend/
│   ├── src/
│   │   ├── components/             # UI components
│   │   ├── hooks/                  # Custom React hooks
│   │   └── types/                  # TypeScript types
│   └── package.json
├── docker-compose.yml
├── .env.example                    # ← copy this to .env
└── README.md
```

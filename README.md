# Job Application Tracker

A backend API for tracking job applications, with an AI-powered job description analyzer and analytics on your job search progress.

**Live demo:** `https://your-app-name.up.railway.app/docs` *(replace with your actual Railway URL)*

Built to explore what a real, production-style backend looks like — proper auth, a tested API, structured data validation, and an AI feature that's actually useful rather than bolted on.

---

## What it does

- **Track applications** — company, role, source, status, and the full job description
- **Full status history** — every status change is logged with a timestamp, not just overwritten, so you can see how long companies actually take to respond
- **AI job description analysis** — paste a job description and get back structured data: required skills, seniority level, key responsibilities, and red flags (e.g. vague scope, unpaid overtime language)
- **Analytics** — response rate, average time-to-first-response, funnel breakdown (Applied → Interviewing → Offer), and conversion rate by application source (LinkedIn vs. Referral, etc.)
- **Secure auth** — JWT-based, hashed passwords, every endpoint scoped to the logged-in user only

---

## Tech stack

| Layer | Choice |
|---|---|
| API | FastAPI |
| Database | PostgreSQL |
| ORM / migrations | SQLAlchemy 2.0 + Alembic |
| Auth | JWT (python-jose) + bcrypt |
| AI | Groq (Llama 3.3 70B) |
| Testing | pytest + FastAPI TestClient |
| Containerization | Docker + Docker Compose |
| Deployment | Railway |
| Frontend | Vanilla HTML/JS (kept intentionally minimal — this is a backend-focused project) |

---

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend   │ ───▶ │   Routers     │ ───▶ │  Services    │
│ (HTML/JS)    │      │ (HTTP layer) │      │ (business    │
└─────────────┘      └──────────────┘      │  logic)      │
                                             └──────┬──────┘
                                                    │
                                     ┌──────────────┼──────────────┐
                                     ▼                              ▼
                              ┌─────────────┐              ┌──────────────┐
                              │  PostgreSQL  │              │  Groq API     │
                              │ (SQLAlchemy) │              │ (AI analysis) │
                              └─────────────┘              └──────────────┘
```

Routers only handle HTTP concerns — parsing requests, returning responses, and status codes. All business logic lives in `services/`, kept separate so it's testable and reusable independent of the HTTP layer.

---

## Design decisions worth knowing about

**Why a separate `status_history` table instead of a single `status` column?**
Overwriting a status field loses information — you'd know an application is "Rejected" but not how long it took to get there. Logging every transition as its own row is what makes the analytics (response time, funnel drop-off) possible at all.

**Why an LLM for job description analysis instead of a trained ML model?**
With realistically only a few dozen applications logged, there isn't nearly enough data to train a supervised model that predicts anything meaningful. Sending the job description to an LLM for structured extraction (skills, seniority, red flags) is a better fit for the actual constraints — it's a language-understanding task, not a statistical prediction task. The `match_score` between required skills and the user's own skills, by contrast, *is* plain deterministic Python — no AI needed for a simple set comparison.

**Why validate the AI's output with Pydantic before storing it?**
LLM output isn't guaranteed to be well-formed. The analyzer service validates the response against a strict schema and fails gracefully (returns a clear "analysis unavailable" state) rather than trusting or silently storing malformed data.

**Why JWT instead of session-based auth?**
Stateless tokens avoid needing server-side session storage, which keeps the API simpler to scale horizontally later — there's no shared session store to coordinate between multiple running instances.

---

## Running it locally

**Requirements:** Docker and Docker Compose.

```bash
git clone https://github.com/your-username/job-application-tracker.git
cd job-application-tracker
cp .env.example .env   # then add your own GROQ_API_KEY
docker compose up --build
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

To run the test suite:
```bash
python -m pytest -v
```

---

## API overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create a new account |
| POST | `/auth/login` | Get an access token |
| POST | `/applications` | Add a job application |
| GET | `/applications` | List your applications |
| GET | `/applications/{id}` | Get one application |
| PATCH | `/applications/{id}/status` | Update status (logs history) |
| DELETE | `/applications/{id}` | Delete an application |
| POST | `/applications/{id}/analyze` | AI-analyze the saved job description |
| GET | `/analytics/summary` | Response rate, avg. time-to-response |
| GET | `/analytics/funnel` | Count of applications per status stage |
| GET | `/analytics/by-source` | Conversion rate by application source |

Full interactive documentation (with request/response schemas) is available at `/docs` once running.

---

## What I'd improve with more time

- Add pagination to `GET /applications` for users with a large number of entries
- Rate-limit the `/analyze` endpoint to control AI API costs at scale
- Add refresh tokens instead of a single fixed-expiry access token
- Expand the frontend beyond a functional single-page demo
- Add integration tests against a real Postgres instance in CI, not just SQLite in-memory

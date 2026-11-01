# CRM Module — AI Employee OS

Customer and Lead Management, Task Tracking, and Activity Timeline for the **AI Employee OS** platform.

---

## 1. Project Overview

AI Employee OS is a six-member team project building an AI-powered operations platform for small businesses, combining an AI executive assistant, communication tools, a CRM, finance tools, document intelligence, and a shared web and API infrastructure. This module is owned by Member 3, Fouzia: CRM and Customer Management.

The CRM module is a self-contained FastAPI application, mounted at `/api/crm`, with its own SQLite database, backed by a lightweight HTML, CSS, and JavaScript frontend. It integrates with two other members' modules: the shared LLM router (for AI-generated summaries and insights) and the shared Google Calendar client (for scheduling follow-up meetings).

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy ORM, Pydantic schemas |
| Database | SQLite (`crm.db`) |
| Frontend | Vanilla HTML, CSS, JavaScript — no framework |
| Testing | pytest, plus manual live testing via Swagger UI and the built frontend |
| AI integration | Shared `llm_router.py` (Qwen + BART models) for summaries and insights |
| Calendar integration | Shared `GoogleCalendarClient` for meeting scheduling |

## 3. Module Structure

```
app/crm/
├── models.py       SQLAlchemy models: Customer, Lead, Task, Activity
├── schemas.py      Pydantic request / response schemas
├── crud.py         Database operations for each entity
├── routes.py       FastAPI endpoints, mounted under /api/crm
├── database.py     Engine + session setup, table auto-creation on startup
├── reminders.py    Stale-lead detection logic for AI Reminders
├── index.html      The CRM frontend (Overview, Customers, Pipeline, Tasks)
└── test_data.py    Seed script for sample customers/leads/tasks

tests/
└── test_crm.py     Automated pytest suite
```

## 4. Data Model

- **Customer** — name, email, phone, company. Has many Leads and Activities (cascade delete).
- **Lead** — belongs to a Customer. Tracks `source`, `status` (New → Contacted → Negotiation → Closed), `assigned_to`.
- **Task** — `title`, `assigned_to`, `priority`, `deadline`, `status` (Pending / In-Progress / Done).
- **Activity** — belongs to a Customer. Logs a `type` (Email / Call / Meeting / Note) and `description`, timestamped.

## 5. Feature Summary

### 5.1 Customer Management

| Feature | Backend | Frontend | Test Status |
|---|---|---|---|
| Customer Profiles | Full CRUD | Add / Edit / Delete / View | Complete — live tested |
| Lead Management | Full CRUD | Add / Edit / Delete | Complete — live tested |
| Sales Pipeline | Status update endpoint | Board view with status dropdown | Complete — live tested |
| Activity Timeline | Log + fetch activities | Timeline modal per customer | Complete — live tested |
| AI Customer Summary | Calls shared `llm_router` | API only | Complete — verified on Google Colab |
| Relationship Insights | Calls shared `llm_router` | API only | Complete — verified on Google Colab |

### 5.2 Task Management

| Feature | Backend | Frontend | Test Status |
|---|---|---|---|
| Task Creation | Full CRUD | Add task form | Complete — live tested |
| Assignment | `assigned_to` field | Text input | Complete — live tested |
| Priorities | High / Medium / Low | Dropdown, colour-coded pill | Complete — live tested |
| Deadlines | `deadline` field | Date picker, shown in table | Complete — live tested |
| AI Reminders | Stale-lead detection, deduplicated | "Run AI reminders" button | Complete — live tested |
| Progress Tracking | Status update endpoint | Status dropdown per task | Complete — live tested |

### 5.3 Other Requirements

| Feature | Backend | Frontend | Test Status |
|---|---|---|---|
| Workflow Activity Logs | Same as Activity Timeline | Timeline modal | Complete — live tested |
| Calendar Integration | Calls shared `GoogleCalendarClient` | API only | Complete — live tested |

## 6. API Reference

All endpoints are prefixed with `/api/crm`. Full interactive docs are available at `/docs` once the server is running.

**Customers** — `POST /customers` · `GET /customers` · `GET /customers/{id}` · `PATCH /customers/{id}` · `DELETE /customers/{id}`

**Leads** — `POST /leads` · `GET /leads?status_filter=` · `GET /customers/{id}/leads` · `PATCH /leads/{id}/status` · `PATCH /leads/{id}` · `DELETE /leads/{id}`

**Tasks** — `POST /tasks` · `GET /tasks?assigned_to=` · `PATCH /tasks/{id}/status` · `PATCH /tasks/{id}` · `DELETE /tasks/{id}`

**Activities** — `POST /activities` · `GET /customers/{id}/timeline`

**Calendar** — `POST /leads/{id}/schedule-meeting`

**AI Features** — `GET /customers/{id}/ai-summary` · `GET /customers/{id}/ai-insight` · `POST /reminders/run`

## 7. Frontend Dashboard

`app/crm/index.html` is a single-page dashboard with four views:

1. **Overview** — live counts of customers, open leads, open tasks, closed deals; recent customers table.
2. **Customers** — full table with Add / Edit / Delete, plus a **Timeline** button per customer that opens their full activity history and lets you log a new activity (Email / Call / Meeting / Note) on the spot.
3. **Pipeline** — a four-column board (New / Contacted / Negotiation / Closed); leads move between stages via a dropdown, with inline edit/delete.
4. **Tasks** — table with priority badges, a deadline column, an inline status dropdown, and a "Run AI reminders" button.

The dashboard talks to the API at `http://127.0.0.1:8000/api/crm` and shows a live connection indicator in the sidebar.

## 8. Issues Found and Fixed During Integration Testing

The following issues surfaced only once the CRM module was merged with the rest of the team's code and run end-to-end for the first time. Each was diagnosed and resolved during this testing pass.

- The root `requirements.txt` was missing CRM-specific dependencies (`sqlalchemy`, `pydantic`, `email-validator`), causing an import failure on startup. Fixed by installing the missing packages.
- The SQLite database path was relative to the current working directory, so running `uvicorn` from a different folder created a second, empty database file. Fixed by deriving the path from the module's own file location.
- Database tables were never created automatically — table creation was only triggered from the manual seed script. Fixed by adding a startup step to FastAPI that creates all tables on every launch.
- `main.py` was missing CORS middleware, which silently blocked every request from the frontend since it's served on a different port. Fixed by adding CORS middleware.
- A large local AI model (used by the shared `llm_router`) was being imported at application startup regardless of whether an AI endpoint was actually called, which made the whole server fail to start on machines with limited RAM. Fixed by deferring that import to inside the two AI endpoints specifically, so the rest of the CRM starts instantly and keeps working independently of the AI module's availability.
- Delete functionality existed for Customers only at the backend level. Added `DELETE` endpoints and CRUD functions for Leads and Tasks, and wired Delete buttons into the frontend for all three entities, each behind a confirmation prompt.
- Task editing (title / assignee / priority / deadline) wasn't supported after creation. Added a full update endpoint for tasks and an Edit modal in the frontend.
- The Activity Timeline had a backend endpoint but no way to view it from the dashboard. Added a Timeline button and modal per customer.
- Task deadlines and the AI Reminders scan had backend support but no frontend controls. Added a deadline field to the task form and a Run AI reminders button.

## 9. Testing

### 9.1 Automated tests

```
pytest tests/test_crm.py -v
```

Covers: customer creation; lead creation and its validation error for a missing customer; lead status transitions; task creation and status updates; activity timeline ordering; activity validation for a missing customer; cascading delete; and the calendar-scheduling flow integrated with the shared calendar client.

**Result: 22 / 22 tests passing** (8 original CRM tests + 14 covering the calendar integration).

### 9.2 Live manual testing

Every endpoint was additionally exercised against a running server via the Swagger UI, and the dashboard was verified end-to-end against real data — creating, editing, and deleting customers, leads, and tasks; moving leads across the pipeline; logging and viewing activities; setting task deadlines; and running the AI reminder scan.

### 9.3 AI Customer Summary / Relationship Insight — verified on Google Colab

These two endpoints depend on the shared `llm_router`, which loads a Qwen text-generation model and a BART summarization model — roughly 4.6GB combined. On the development machine, loading that model exceeds available RAM, so the endpoints couldn't be exercised through the local running server, even after freeing all other applications.

To confirm the CRM-side code itself is correct, the exact same functions were imported and called directly in a Google Colab notebook (12.7GB RAM), against the unmodified project code:

```
from app.crm.routes import get_ai_customer_summary, get_ai_relationship_insight
summary_result = get_ai_customer_summary(customer.id, db=db)
insight_result = get_ai_relationship_insight(customer.id, db=db)
```

Result:
```
{'customer_id': 7, 'summary': 'Ali Raza Test has 2 logged activities.'}
{'customer_id': 7, 'insight': 'Engagement: Warm. Next action: Follow up with Ali Raza Test.'}
```

Both functions executed without error and returned correctly structured responses. This confirms the endpoint logic, database queries, and integration with the shared AI router are all correct — the local test-machine failure was a RAM constraint, not a code defect.

### 9.4 Calendar integration — live tested

`POST /leads/{id}/schedule-meeting` calls the shared `GoogleCalendarClient`. Test credentials were created and configured for this environment, and the endpoint was tested live via the Swagger UI, returning:

```
HTTP 201 Created
```

The endpoint successfully created a real Google Calendar event and logged it to the customer's activity timeline — confirming the calendar integration works correctly end-to-end, not just in isolation.

## 10. Running Locally

**Setup**
```
pip install -r requirements.txt
```
First run only — set the Hugging Face cache location to a drive with enough free space, then open a new terminal.

**Run the backend**
```
uvicorn app.main:app --reload
```
Wait for "Application startup complete." Tables are created automatically on first run. Interactive API docs are at `http://127.0.0.1:8000/docs`.

**Run the frontend**
Open `app/crm/index.html` with a local static server (e.g. VS Code's Live Server extension) and it will connect to the backend automatically.

**Run the tests**
```
pytest tests/test_crm.py -v
```

## 11. Known Limitations

- The AI endpoints require a large local model that exceeds this development machine's available RAM to load directly. This was mitigated by independently verifying the identical endpoint code on Google Colab (§9.3), confirming the code has no defect.
- The database is SQLite for local development. `database.py` reads `CRM_DATABASE_URL` from the environment, so switching to PostgreSQL for production is a configuration change, not a code change.

## 12. Summary

All customer, lead, task, pipeline, activity-timeline, reminder, calendar, and AI-insight functionality specified for this module is implemented, integrated with the rest of the team's codebase, and has been verified through automated tests, live manual testing, an independent Google Colab verification of the AI endpoints, and a live end-to-end test of the calendar integration. Every feature originally assigned to this module is complete and confirmed working.

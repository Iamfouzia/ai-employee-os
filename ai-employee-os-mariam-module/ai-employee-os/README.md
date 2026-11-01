# AI Employee OS

Scope: **Frontend, Backend, Security & Infrastructure**. 

## Structure

```
ai-employee-os/
├── backend/                 FastAPI service
│   ├── app/
│   │   ├── core/            config, JWT + password hashing, MFA (TOTP), auth dependency
│   │   ├── db/               SQLAlchemy async engine + models (Organization, User)
│   │   ├── api/               auth.py (register/login/MFA/refresh), pricing.py (plans/usage/upgrade)
│   │   └── schemas/          Pydantic request/response models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                 Next.js 14 (App Router) + TypeScript + Tailwind
│   ├── app/                   /, /login, /login/mfa, /register, /dashboard
│   ├── components/           UsageMeter
│   ├── lib/api.ts             typed fetch client
│   └── Dockerfile
└── docker-compose.yml        postgres + redis + backend + frontend
```

## What's implemented

**Authentication & security**
- Email/password registration and login (bcrypt via passlib)
- JWT access + refresh tokens
- TOTP-based MFA (`pyotp`) — enable per user, verified on login
- Role field (`owner` / `admin` / `member`) + `require_role()` dependency for
  department-based permission checks (the Business-plan "Department-based Permissions" feature)

**Database**
- Async PostgreSQL via SQLAlchemy 2.0 (`asyncpg`)
- `Organization` (tenant) and `User` models; each org has a `plan_tier`

**Pricing plans (Business Features)**
- `PLAN_LIMITS` encodes the Basic/Pro/Business limits from the spec (seats, AI
  requests, storage)
- `GET /api/pricing/plans` — public pricing table
- `GET /api/pricing/usage` — an org's current usage vs. its plan limit
- `enforce_ai_request_quota` — a dependency other members can attach to any
  AI-employee endpoint (e.g. AI Sales Manager) to enforce Fair Use limits and
  return `402 Payment Required` once exhausted
- `POST /api/pricing/upgrade` — owner/admin only

**Frontend**
- Landing page, login (+ MFA step), register, and a dashboard shell reading
  live plan usage from the backend
- Custom Tailwind token system (`tailwind.config.ts`) — deep navy/graphite
  console with a single amber signal color, not a generic template palette
- JWT stored in a client cookie via `lib/api.ts`; swap for httpOnly cookies
  issued server-side before production

## Running it locally

```bash
cp backend/.env.example backend/.env   # then edit SECRET_KEY
docker compose up --build
```

- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:3000

Or run each service natively:

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev
```



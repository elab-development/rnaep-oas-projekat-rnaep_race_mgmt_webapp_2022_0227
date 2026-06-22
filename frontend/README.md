# ObstaRace Frontend

Vite + React + TypeScript SPA for the ObstaRace microservices platform.

## Prerequisites

- Node.js 20+
- Docker Compose stack running (`nginx`, `user-service`, `race-service`, `payment-service`) on port **80**

## Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App runs at `http://localhost:5173`. Vite dev server proxies API paths to `VITE_API_BASE_URL` (default `http://localhost:80`).

## Environment variables

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Nginx gateway URL (production build / proxy target) |

## Scripts

- `npm run dev` — local development
- `npm run build` — production bundle
- `npm run preview` — preview production build
- `npm run lint` — ESLint
- `npm run format` — Prettier

## Auth

Login uses `POST /api/users/auth/login`, which sets an **httponly** `access_token` cookie. The Axios client sends cookies via `withCredentials: true`. Session user data comes from `GET /api/users/me` on bootstrap and after login.

## Payment return URLs

Configure PaymentService env vars to point at the frontend:

- `PAYMENT_SUCCESS_URL` → `http://localhost:5173/payment-success?registration_id=REG_ID&session_id={CHECKOUT_SESSION_ID}`
- `PAYMENT_CANCEL_URL` → `http://localhost:5173/payment-failed?registration_id=REG_ID`

Both pages use a 4-state UI (`loading` → `success` | `failed` | `timeout`). Polling stops automatically after ~25s; timeout shows an amber state with **Refresh status**.

## API route coverage (UI)

| Endpoint | UI entry point |
|---|---|
| `GET /api/race/` | Browse Races, Organiser Dashboard (client-filtered by `organiser_id`) |
| `GET /api/race/{id}` | Race Detail, Edit Race |
| `POST /api/race/` | Create Race form |
| `PATCH /api/race/{id}` | Edit Race form |
| `DELETE /api/race/{id}` | Organiser Dashboard / Edit Race delete modal |
| `GET /api/registration/myregistrations` | My Registrations |
| `GET /api/registration/?race_id=` | Organiser race registrations page |
| `POST /api/registration/` | Register on Race Detail |
| `DELETE /api/registration/{id}` | Cancel on My Registrations / payment-failed |
| `POST /payments/checkout` | After register, retry payment flows |
| `GET /payments/me` | My Payments, payment polling |
| `GET /payments/{id}` | Payment polling |
| `POST /api/users/auth/login` | Login page |
| `POST /api/users/auth/register/*` | Register page (participant + organiser) |
| `POST /api/users/auth/logout` | Navbar Logout |
| `GET /api/users/me` | App bootstrap / auth store |

## Race data

Browse Races and Organiser Dashboard load exclusively from `GET /api/race/`. Race Detail loads from `GET /api/race/{id}`. Race queries use `staleTime: 0` so each visit refetches from the API. On failure, pages show an error state with toast + Retry — no silent fallbacks.

## Known backend issues

- **`RaceResponse` has no live registration count** — browse/detail pages show capacity only; spots remaining cannot be computed without an extra field or API.
- **`RegistrationResponse` has no participant name** — organiser registration tables show `Participant #{id}` until the backend adds name fields.
- **`PAYMENT_SUCCESS_URL` / `PAYMENT_CANCEL_URL` do not append query params in PaymentService code** — ops must include `registration_id` / `session_id` in the env URL template.
- **Registration `payment_status` vs Payment record `status`** — different enums/services; UI labels match each source.

## Nginx reminder

Add `proxy_set_header Cookie $http_cookie;` to `/api/race/` and `/api/registration/` locations so JWT cookies reach RaceService.

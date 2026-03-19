# Issue: Astro dev logs ECONNREFUSED calling backend

## Summary
Running `npm run dev` in the frontend can show a large `ECONNREFUSED` stack trace when the backend API is not reachable at `PUBLIC_API_BASE` (default `http://localhost:8000`). This commonly happens when the backend is not running, is running on a different port, or is bound to a different host/interface.

This is not an Astro bug; it is the frontend SSR calling the API during page render.

## Environment
- Frontend: Astro (SSR routes present)
- Backend: FastAPI
- OS: Windows
- Default API base: `PUBLIC_API_BASE=http://localhost:8000`

## Repro
1. Start frontend only:
   - `cd frontend`
   - `npm run dev`
2. Visit `http://localhost:4321/`
3. Observe console output:
   - `[api] fetch failed ... code: 'ECONNREFUSED'` and an undici stack trace

## Expected
- If backend is down: frontend should keep rendering pages that can tolerate missing data, and the console log should be concise and actionable.

## Actual
- A large stack trace is printed, which looks like a crash.

## Root Cause
- The homepage does an SSR fetch: `api("/articles?limit=5")`.
- When the backend is not reachable, Node’s fetch (undici) throws `ECONNREFUSED`.
- Logging the raw error object prints a large stack trace.

## Definitive Fix
### 1) Ensure backend is running on the same host/port as `PUBLIC_API_BASE`
Recommended dev run command (from `backend/`):
- `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

Sanity check:
- Open `http://localhost:8000/docs` (should load FastAPI docs)

If your backend uses a different port/host, update [frontend/.env](../../frontend/.env):
- `PUBLIC_API_BASE=http://127.0.0.1:8000`

### 2) Make the log non-alarming
Keep a single concise warning and avoid printing the raw undici error stack.

## Notes
- Astro warning about “no adapter installed” is expected during dev; you only need an adapter for production builds.

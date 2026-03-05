~/.bun/bin/bun run dev# Active Context: Inventory Management System

## Current State

**Project Status**: ✅ Ready for development in GitHub Codespaces

Full-stack Inventory Management System with FastAPI backend and Next.js frontend.

## Recently Completed

- [x] GitHub Codespaces setup completed
- [x] Bun package manager installed
- [x] Frontend dependencies installed (bun install)
- [x] Backend Python dependencies installed (pip install)
- [x] SQLite database configured for Codespaces
- [x] Environment variables configured (.env, .env.local)
- [x] Type check and lint passing
- [x] Backend server verified working

## Current Structure

| File/Directory | Purpose | Status |
|----------------|---------|--------|
| `src/app/` | Next.js frontend pages | ✅ Ready |
| `src/components/` | React components | ✅ Ready |
| `src/lib/api.ts` | API client | ✅ Ready |
| `backend/app/` | FastAPI backend | ✅ Ready |
| `backend/.env` | Backend config (SQLite) | ✅ Ready |
| `.env.local` | Frontend API URL | ✅ Ready |

## Running the Application

### Start the Backend:
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Backend will be available at http://localhost:8000

### Start the Frontend:
```bash
~/.bun/bin/bun run dev
```
Frontend will be available at http://localhost:3000

## Environment Configuration

### Backend (`backend/.env`):
- Database: SQLite (`sqlite+aiosqlite:///./inventory.db`)
- API docs: http://localhost:8000/docs
- CORS configured for localhost:3000

### Frontend (`.env.local`):
- API URL: http://localhost:8000/api/v1

## Session History

| Date | Changes |
|------|---------|
| Initial | Template created with base setup |
| 2026-03-05 | GitHub Codespaces setup completed, full-stack app ready |
| 2026-03-05 | Currency changed from USD ($) to Philippine Peso (₱) |
| 2026-03-05 | Added category management system (create, edit, delete categories) |
| 2026-03-05 | Activated login/logout functionality with JWT authentication |
| 2026-03-05 | Fixed CORS configuration for GitHub Codespaces |
| 2026-03-05 | Fixed API URL configuration for GitHub Codespaces forwarded ports |
- [ ] Add testing setup recipe

## Session History

| Date | Changes |
|------|---------|
| Initial | Template created with base setup |

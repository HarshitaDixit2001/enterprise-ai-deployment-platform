# Enterprise AI Platform — Frontend

React and TypeScript dashboard for the Enterprise AI Deployment & Evaluation Platform. Built with Vite and Recharts.

## Features

- Use-case management
- AI evaluation results and metrics
- Candidate comparison and release governance
- Release audit history
- Health, readiness, and observability views

## Prerequisites

- Node.js and npm
- The FastAPI backend running locally at `http://127.0.0.1:8000`

## Getting Started

From this directory, install dependencies and start the development server:

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

The Vite development server proxies API requests to the local FastAPI backend. Start the backend separately from the repository root:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Validation

Run ESLint:

```powershell
npm run lint
```

Run the TypeScript checks and production build:

```powershell
npm run build
```

The production assets are generated in `dist/`.

## Related Documentation

See the repository-root `README.md` for the overall architecture, evaluation workflow, release governance, API endpoints, and project limitations.

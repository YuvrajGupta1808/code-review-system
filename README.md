# Code Review System

Multi-agent Python code analysis with real-time streaming events, plus a React-based UI.

## Repo Layout

- `backend/`: FastAPI backend, agents, and event streaming
- `frontend/`: React + TypeScript streaming UI
- `docs/`: Documentation (architecture, setup, UI/streaming specs)
- `plan/`: Implementation plan(s)
- `tests/`: Automated tests

## Quickstart

### Backend (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
python backend/main.py
```

The server defaults to `http://0.0.0.0:8000`.

Real-time endpoints:
- WebSocket: `/ws/review`
- SSE: `/stream/review`

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Vite dev server typically runs at `http://localhost:5173`.

### Tests

```bash
pytest -q
```

## Further Reading

See `docs/` for architecture and setup details, and `plan/` for implementation notes.


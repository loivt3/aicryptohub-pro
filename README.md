# AI Crypto Hub Pro

> Microservices-based SaaS Platform for Cryptocurrency Trading Analysis

## Architecture

```
aicryptohub-pro/
├── backend/          # Python FastAPI
├── frontend/         # Vue.js 3 + Vite
├── database/         # PostgreSQL Migrations
└── infrastructure/   # Docker, Nginx
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Frontend**: Vue.js 3, Vite, Pinia, Vue Router
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL (Supabase)
- **Auth**: Supabase Auth / JWT
- **Real-time**: WebSocket (Binance streams)
- **AI**: Gemini, DeepSeek

## API Documentation

After starting the backend, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

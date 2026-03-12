# AMADOP Blogging Platform - Setup Guide

## Project Overview

This is a microservices-based blogging platform with:
- 4 Python/FastAPI backend services
- React/TypeScript frontend with Vite
- PostgreSQL database
- Docker Compose orchestration

## Directory Structure

```
amadop-blogging-platform/
├── backend/
│   ├── auth_service/          # Port 8001 - Authentication & JWT
│   ├── post_service/          # Port 8002 - Blog posts
│   ├── comment_service/       # Port 8003 - Comments
│   └── notification_service/  # Port 8004 - Notifications
├── frontend/                  # Port 5173 - React UI
├── docker-compose.yml
└── README.md
```

## Setup Instructions

### Option 1: Docker Compose (Recommended)

1. **Start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend services: http://localhost:8001-8004
   - API docs: http://localhost:8001/docs (and 8002, 8003, 8004)

3. **Stop services:**
   ```bash
   docker-compose down
   ```

### Option 2: Local Development

#### Backend Services

Each service needs to be run separately:


**Terminal 1 - Database:**
```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=amadop_db postgres:15-alpine
```

**Terminal 2 - Auth Service:**
```bash
cd backend/auth_service
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**Terminal 3 - Post Service:**
```bash
cd backend/post_service
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

**Terminal 4 - Comment Service:**
```bash
cd backend/comment_service
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
```

**Terminal 5 - Notification Service:**
```bash
cd backend/notification_service
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8004
```

#### Frontend

**Terminal 6 - Frontend:**
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Testing the Application

1. **Register a user:** Navigate to http://localhost:5173/register
2. **Login:** Use your credentials at http://localhost:5173/login
3. **Create a post:** Click "Create Post" in the navbar
4. **Add comments:** View a post and add comments
5. **Check notifications:** Click "Notifications" to see comment notifications

## Health Checks

Check if services are running:
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

## Metrics

View Prometheus metrics:
```bash
curl http://localhost:8001/metrics
```

## Troubleshooting

- **Database connection errors:** Ensure PostgreSQL is running and accessible
- **CORS errors:** Check CORS_ORIGINS in .env files
- **Port conflicts:** Ensure ports 5173, 8001-8004, 5432 are available
- **Module not found:** Run `pip install -r requirements.txt` or `npm install`

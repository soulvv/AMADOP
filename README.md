# AMADOP Blogging Platform

A modern microservices-based blogging platform with 4 backend services and a React frontend.

## Architecture

- **Auth Service** (Port 8001): User authentication and JWT management
- **Post Service** (Port 8002): Blog post CRUD operations
- **Comment Service** (Port 8003): Comment management
- **Notification Service** (Port 8004): User notifications
- **Frontend** (Port 5173): React + Vite + TailwindCSS
- **Database**: PostgreSQL

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker Compose

1. Clone the repository
2. Start all services:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:5173
   - Auth Service: http://localhost:8001
   - Post Service: http://localhost:8002
   - Comment Service: http://localhost:8003
   - Notification Service: http://localhost:8004

### Local Development

#### Backend Services
Each service can be run independently:

```bash
cd backend/auth_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Copy `.env.example` files in each service directory and configure as needed.

## API Documentation

- Auth Service: http://localhost:8001/docs
- Post Service: http://localhost:8002/docs
- Comment Service: http://localhost:8003/docs
- Notification Service: http://localhost:8004/docs

## Monitoring

- Health checks: `GET /health` on each service
- Metrics: `GET /metrics` on each service (Prometheus format)

## Project Structure

```
.
├── backend/
│   ├── auth_service/
│   ├── post_service/
│   ├── comment_service/
│   └── notification_service/
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── context/
│       └── types/
└── docker-compose.yml
```

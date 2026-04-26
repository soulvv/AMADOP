# AMADOP - Autonomous Multi-Agent DevOps Orchestration Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

A modern, microservices-based blogging platform built with Python/FastAPI backend services and React frontend. This project demonstrates enterprise-grade architecture with proper separation of concerns, observability, and DevOps best practices.

## 🏗️ Architecture Overview

The platform consists of 4 independent microservices and a React frontend:

- **🔐 Auth Service** (Port 8001): JWT authentication and user management
- **📝 Post Service** (Port 8002): Blog post CRUD operations
- **💬 Comment Service** (Port 8003): Comment management with notifications
- **🔔 Notification Service** (Port 8004): User notification system
- **🌐 Frontend** (Port 5173): React + TypeScript + TailwindCSS
- **🗄️ Database**: PostgreSQL with proper indexing

## ✨ Features

- ✅ **User Authentication**: Secure JWT-based authentication
- ✅ **Blog Management**: Create, read, and delete blog posts
- ✅ **Interactive Comments**: Comment system with real-time notifications
- ✅ **Responsive UI**: Modern, mobile-friendly interface
- ✅ **Microservices Architecture**: Independent, scalable services
- ✅ **Health Monitoring**: Health checks and Prometheus metrics
- ✅ **Docker Support**: Full containerization with Docker Compose
- ✅ **API Documentation**: Auto-generated Swagger/OpenAPI docs

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (Recommended)
- **Node.js 18+** (for local development)
- **Python 3.11+** (for local development)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/soulvv/AMADOP.git
cd AMADOP

# Switch to project branch for full code
git checkout project

# Start all services
docker compose up --build

# Access the application
open http://localhost:5173
```

### Option 2: Local Development

```bash
# Backend services (run each in separate terminal)
cd backend/auth_service && pip install -r requirements.txt && uvicorn main:app --reload --port 8001
cd backend/post_service && pip install -r requirements.txt && uvicorn main:app --reload --port 8002
cd backend/comment_service && pip install -r requirements.txt && uvicorn main:app --reload --port 8003
cd backend/notification_service && pip install -r requirements.txt && uvicorn main:app --reload --port 8004

# Frontend
cd frontend && npm install && npm run dev
```

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main application |
| **Auth API** | http://localhost:8001/docs | Authentication API docs |
| **Post API** | http://localhost:8002/docs | Blog post API docs |
| **Comment API** | http://localhost:8003/docs | Comment API docs |
| **Notification API** | http://localhost:8004/docs | Notification API docs |
| **AI Service** | http://localhost:8005/docs | AI agents API docs |
| **Grafana** | http://localhost:3000 | Monitoring dashboards |
| **Prometheus** | http://localhost:9090 | Metrics collection |

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **JWT** - JSON Web Tokens for authentication
- **Bcrypt** - Password hashing
- **Prometheus** - Metrics collection
- **OpenAI GPT-4o-mini** - AI summarization & moderation
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client

### DevOps & Monitoring
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Kubernetes (Minikube)** - Container orchestration with HPA
- **Prometheus** - Metrics scraping & alerting
- **Grafana** - Visual monitoring dashboards
- **Health Checks** - Service monitoring
- **Structured Logging** - JSON-formatted logs

## 📁 Project Structure

```
AMADOP/
├── backend/
│   ├── auth_service/          # Authentication microservice
│   ├── post_service/          # Blog post microservice
│   ├── comment_service/       # Comment microservice
│   ├── notification_service/  # Notification microservice
│   └── ai_service/            # Autonomous AI agents
│       ├── agents/
│       │   ├── content_agent.py   # Summarization + Moderation
│       │   └── devops_agent.py    # Health monitoring + Anomaly detection
│       ├── main.py
│       ├── routes.py
│       └── Dockerfile
├── frontend/                  # React frontend application
├── k8s/                       # Kubernetes manifests
├── monitoring/                # Prometheus & Grafana configs
├── docker-compose.yml         # Docker orchestration
└── README.md                  # This file
```

## 🔧 Configuration

Each service uses environment variables for configuration. Copy `.env.example` files and customize:

```bash
# Database connection
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/amadop_db

# JWT secret (change in production!)
SECRET_KEY=your-secret-key-change-in-production

# Service URLs for inter-service communication
AUTH_SERVICE_URL=http://localhost:8001
POST_SERVICE_URL=http://localhost:8002
```

## 📊 Monitoring & Observability

- **Health Checks**: `GET /health` on each service
- **Metrics**: `GET /metrics` (Prometheus format)
- **Structured Logs**: JSON-formatted application logs
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Grafana Dashboards**: Service health, CPU, memory, HTTP errors
- **Prometheus**: Metrics scraping with pod annotations

## 🤖 Autonomous AI Agents

The platform includes 3 AI agents powered by OpenAI GPT-4o-mini (with rule-based fallbacks):

### Content Intelligence Agent
- **Auto-Summarization**: Generates topic-based summaries for every blog post
- **Endpoint**: `POST /api/v1/ai/summarize`

### Content Moderation Agent
- **Profanity Filter**: Scans comments for toxic language and replaces with `****`
- **40+ toxic words** covered with case-insensitive regex matching
- **Endpoint**: `POST /api/v1/ai/moderate`

### DevOps Self-Healing Agent
- **Health Monitoring**: Pings all microservices and reports status + response times
- **Anomaly Detection**: Detects service downtime, high latency (>2s), and CPU spikes
- **Endpoints**: `GET /api/v1/ai/health-check`, `GET /api/v1/ai/anomalies`

## 🧪 Testing

```bash
# Run backend tests
cd backend/auth_service && pytest
cd backend/post_service && pytest

# Run frontend tests
cd frontend && npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**soulvv** - [GitHub Profile](https://github.com/soulvv)

## 🙏 Acknowledgments

- Built with [Kiro AI](https://kiro.ai) - AI-powered development assistant
- Inspired by modern microservices architecture patterns
- Thanks to the open-source community for the amazing tools

---

⭐ **Star this repository if you found it helpful!**

# AMADOP Blogging Platform - Quick Start Guide

## ⚠️ Important Note About Python 3.13

You're running Python 3.13.7, which is very new. Some Python packages (like `pydantic-core` and `cryptography`) don't have pre-built wheels for Python 3.13 yet and require Rust/Cargo to compile from source.

## Recommended Solutions

### Option 1: Use Docker (Recommended - Easiest)

Docker will handle all dependencies automatically.

1. **Make sure Docker Desktop is running** (check the system tray for the Docker whale icon)

2. **Close and reopen your terminal** to refresh the PATH

3. **Run the platform**:
   ```bash
   docker compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Auth API: http://localhost:8001/docs
   - Post API: http://localhost:8002/docs
   - Comment API: http://localhost:8003/docs
   - Notification API: http://localhost:8004/docs

### Option 2: Install Python 3.11

Python 3.11 has pre-built wheels for all packages.

1. **Download Python 3.11**:
   ```bash
   winget install Python.Python.3.11
   ```

2. **Create virtual environments with Python 3.11**:
   ```bash
   py -3.11 -m venv backend/auth_service/venv
   py -3.11 -m venv backend/post_service/venv
   py -3.11 -m venv backend/comment_service/venv
   py -3.11 -m venv backend/notification_service/venv
   ```

3. **Run the setup script**:
   ```powershell
   .\start-services.ps1
   ```

4. **Start all services**:
   ```powershell
   .\run-all-services.ps1
   ```

### Option 3: Install Rust/Cargo (Advanced)

If you want to use Python 3.13, you need to install Rust.

1. **Install Rust**:
   ```bash
   winget install Rustlang.Rustup
   ```

2. **Close and reopen your terminal**

3. **Verify Rust installation**:
   ```bash
   cargo --version
   ```

4. **Run the setup script**:
   ```powershell
   .\start-services.ps1
   ```

5. **Start all services**:
   ```powershell
   .\run-all-services.ps1
   ```

## What's Included

### Backend Services (Python/FastAPI)
- **Auth Service** (Port 8001) - User registration, login, JWT authentication
- **Post Service** (Port 8002) - Blog post CRUD operations
- **Comment Service** (Port 8003) - Comment management with notifications
- **Notification Service** (Port 8004) - User notifications

### Frontend (React + TypeScript + TailwindCSS)
- **Port 5173** - Modern blogging UI with authentication

### Features
✅ User registration and login  
✅ JWT token authentication  
✅ Create, read, delete blog posts  
✅ Comment on posts  
✅ Real-time notifications  
✅ Health checks on all services  
✅ Prometheus metrics endpoints  
✅ Responsive UI with TailwindCSS  

## Testing the System

### 1. Check Service Health
```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

### 2. Register a User
```bash
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### 3. Login
```bash
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

### 4. Use the Frontend
Open http://localhost:5173 in your browser and:
- Register a new account
- Login
- Create blog posts
- Comment on posts
- View notifications

## Troubleshooting

### Docker not found
- Make sure Docker Desktop is installed and running
- Close and reopen your terminal
- Try `docker --version` to verify

### PostgreSQL connection errors
- Make sure PostgreSQL service is running
- Check the DATABASE_URL in .env files
- Default: `postgresql://postgres:postgres@localhost:5432/amadop_db`

### Port already in use
- Check if another application is using ports 8001-8004 or 5173
- Stop the conflicting application or change ports in the code

### Frontend not loading
- Make sure all backend services are running
- Check browser console for errors
- Verify CORS settings in backend services

## Next Steps

1. **Explore the API Documentation**:
   - http://localhost:8001/docs (Auth API)
   - http://localhost:8002/docs (Post API)
   - http://localhost:8003/docs (Comment API)
   - http://localhost:8004/docs (Notification API)

2. **Monitor with Prometheus**:
   - http://localhost:8001/metrics
   - http://localhost:8002/metrics
   - http://localhost:8003/metrics
   - http://localhost:8004/metrics

3. **Read the Full Documentation**:
   - See README.md for detailed architecture
   - See SETUP.md for development setup

## Support

For issues or questions:
1. Check the logs in the terminal windows
2. Review the README.md and SETUP.md files
3. Check service health endpoints
4. Verify all environment variables are set correctly

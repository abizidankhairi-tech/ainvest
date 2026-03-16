#!/bin/bash

# INVESTAI - Project Initialization Script
# This script sets up your complete development environment

set -e  # Exit on error

echo "🚀 InvestAI - Project Initialization"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create project directory structure
echo "📁 Creating project structure..."

mkdir -p backend/{api,models,services,auth,tasks,utils,alembic/versions,tests/{unit,integration,e2e}}
mkdir -p frontend/{pages,components,assets/images,utils}
mkdir -p docs/{user,dev}

echo "✅ Project structure created"
echo ""

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Docker
docker-compose.override.yml

# Database
*.db
*.sqlite

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Coverage
htmlcov/
.coverage
.pytest_cache/

# Misc
*.bak
*.tmp
EOF

echo "✅ .gitignore created"
echo ""

# Create .env.example
echo "📝 Creating .env.example..."
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql://investai:password@postgres:5432/investai

# Redis
REDIS_URL=redis://redis:6379/0

# Security (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=change-this-to-a-random-32-character-string-in-production

# APIs
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Email (SendGrid)
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=noreply@investai.app

# SMS (Twilio) - Optional
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Application
BACKEND_URL=http://backend:8000
FRONTEND_URL=http://localhost:8050
ENVIRONMENT=development
EOF

echo "✅ .env.example created"
echo ""

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created (remember to add your API keys!)"
else
    echo "⚠️  .env already exists, skipping..."
fi
echo ""

# Create docker-compose.yml
echo "🐳 Creating docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: investai_postgres
    environment:
      POSTGRES_USER: investai
      POSTGRES_PASSWORD: password
      POSTGRES_DB: investai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U investai"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: investai_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: investai_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://investai:password@postgres:5432/investai
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      GROQ_API_KEY: ${GROQ_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SENDGRID_API_KEY: ${SENDGRID_API_KEY}
      SENDGRID_FROM_EMAIL: ${SENDGRID_FROM_EMAIL}
      TWILIO_ACCOUNT_SID: ${TWILIO_ACCOUNT_SID}
      TWILIO_AUTH_TOKEN: ${TWILIO_AUTH_TOKEN}
      TWILIO_PHONE_NUMBER: ${TWILIO_PHONE_NUMBER}
      ENVIRONMENT: ${ENVIRONMENT:-development}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: investai_frontend
    ports:
      - "8050:8050"
    environment:
      BACKEND_URL: http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
    command: python app.py

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: investai_celery_worker
    environment:
      DATABASE_URL: postgresql://investai:password@postgres:5432/investai
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      GROQ_API_KEY: ${GROQ_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: celery -A celery_app worker --loglevel=info

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: investai_celery_beat
    environment:
      DATABASE_URL: postgresql://investai:password@postgres:5432/investai
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: celery -A celery_app beat --loglevel=info

volumes:
  postgres_data:
  redis_data:
EOF

echo "✅ docker-compose.yml created"
echo ""

# Create backend Dockerfile
echo "🐳 Creating backend Dockerfile..."
mkdir -p backend
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

echo "✅ backend/Dockerfile created"
echo ""

# Create frontend Dockerfile
echo "🐳 Creating frontend Dockerfile..."
mkdir -p frontend
cat > frontend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8050

CMD ["python", "app.py"]
EOF

echo "✅ frontend/Dockerfile created"
echo ""

# Create backend requirements.txt
echo "📦 Creating backend/requirements.txt..."
cat > backend/requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic[email]==2.5.3
redis==5.0.1
celery==5.3.4
groq==0.4.1
openai==1.10.0
yfinance==0.2.35
pandas==2.1.4
pillow==10.2.0
pytesseract==0.3.10
sendgrid==6.11.0
twilio==8.11.0
sentry-sdk==1.40.0
python-dotenv==1.0.0
EOF

echo "✅ backend/requirements.txt created"
echo ""

# Create frontend requirements.txt
echo "📦 Creating frontend/requirements.txt..."
cat > frontend/requirements.txt << 'EOF'
dash==2.14.2
dash-bootstrap-components==1.5.0
plotly==5.18.0
requests==2.31.0
pandas==2.1.4
python-dotenv==1.0.0
EOF

echo "✅ frontend/requirements.txt created"
echo ""

# Create README.md
echo "📝 Creating README.md..."
cat > README.md << 'EOF'
# 🚀 InvestAI - AI-Powered IDX Portfolio Manager

AI-powered portfolio management platform for Indonesian stocks with breakthrough **30-second portfolio import** via screenshot.

## ✨ Key Features

- 📸 **Image Import** - Screenshot → Portfolio in 30 seconds
- 🤖 **AI Advisor** - Powered by Groq Llama 3.3 70B
- 📊 **Real-time Tracking** - Live price updates every 60 seconds
- 🎯 **Strategy Builder** - Plan multi-zone entries & tiered exits
- 🔔 **Smart Alerts** - Email, SMS, and in-app notifications
- 📈 **Advanced Analytics** - Risk-adjusted returns, sector analysis

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- API Keys: Groq, OpenAI (for image OCR)

### Installation

1. Clone the repository
```bash
git clone <your-repo-url>
cd investai
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Start services
```bash
docker-compose up -d
```

4. Run database migrations
```bash
docker-compose exec backend alembic upgrade head
```

5. Access the application
- Frontend: http://localhost:8050
- Backend API: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 📖 Documentation

- [Master Development Plan](INVESTAI_MASTER_PLAN.md)
- [Quick Reference Guide](QUICK_REFERENCE.md)
- [API Documentation](http://localhost:8000/docs) (when running)

## 🏗️ Architecture

```
Frontend (Dash) → Backend (FastAPI) → PostgreSQL
                       ↓
                  Groq AI (Llama 3.3 70B)
                  OpenAI (GPT-4 Vision)
                       ↓
                  Celery (Background Tasks)
                       ↓
                  Redis (Cache & Queue)
```

## 🛠️ Development

### Useful Commands

```bash
# View logs
docker-compose logs -f

# Access PostgreSQL
docker-compose exec postgres psql -U investai -d investai

# Run tests
docker-compose exec backend pytest

# Restart a service
docker-compose restart backend
```

### Project Structure

```
investai/
├── backend/          # FastAPI application
├── frontend/         # Dash application
├── docs/            # Documentation
└── docker-compose.yml
```

## 🧪 Testing

```bash
# Run all tests
docker-compose exec backend pytest tests/ -v

# Test coverage
docker-compose exec backend pytest --cov=. --cov-report=html
```

## 🚀 Deployment

See [Deployment Guide](docs/dev/deployment.md) for production deployment instructions.

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [Dash](https://dash.plotly.com/)
- AI by [Groq](https://groq.com/) & [OpenAI](https://openai.com/)

---

**Status:** 🚧 In Development  
**Version:** 1.0.0-alpha  
**Last Updated:** February 2026
EOF

echo "✅ README.md created"
echo ""

# Initialize Git repository
if [ ! -d .git ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial project setup"
    echo "✅ Git repository initialized"
else
    echo "⚠️  Git repository already exists, skipping..."
fi
echo ""

# Display next steps
echo ""
echo "=================================="
echo "✅ Project Initialization Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit .env file and add your API keys:"
echo "   - GROQ_API_KEY (get from https://console.groq.com)"
echo "   - OPENAI_API_KEY (get from https://platform.openai.com)"
echo ""
echo "2. Start the development environment:"
echo "   docker-compose up -d"
echo ""
echo "3. Run database migrations:"
echo "   docker-compose exec backend alembic upgrade head"
echo ""
echo "4. Access the application:"
echo "   Frontend: http://localhost:8050"
echo "   Backend API: http://localhost:8000/docs"
echo ""
echo "5. Read the documentation:"
echo "   - Master Plan: INVESTAI_MASTER_PLAN.md"
echo "   - Quick Reference: QUICK_REFERENCE.md"
echo ""
echo "🚀 Happy coding!"
echo ""

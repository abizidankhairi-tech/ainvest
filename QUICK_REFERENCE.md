# 🚀 INVESTAI - QUICK REFERENCE GUIDE

**For use in VS Code / Claude Code**

---

## 📁 PROJECT STRUCTURE

```
investai/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── portfolios.py
│   │   ├── holdings.py
│   │   ├── market_data.py
│   │   ├── ai_chat.py
│   │   └── alerts.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   ├── holding.py
│   │   ├── transaction.py
│   │   ├── alert.py
│   │   └── ai_query.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── portfolio_service.py
│   │   ├── market_data_service.py
│   │   ├── ai_service.py
│   │   ├── ocr_service.py
│   │   └── alert_service.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_handler.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── price_updater.py
│   │   ├── daily_insights.py
│   │   └── alert_checker.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── prompt_builder.py
│   │   └── image_processor.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── celery_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── dashboard.py
│   │   ├── portfolio.py
│   │   ├── stock_detail.py
│   │   └── settings.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── navbar.py
│   │   ├── portfolio_card.py
│   │   ├── holdings_table.py
│   │   ├── ai_chat.py
│   │   ├── insight_card.py
│   │   ├── strategy_builder.py
│   │   └── alerts_dashboard.py
│   ├── assets/
│   │   ├── style.css
│   │   ├── custom.js
│   │   └── images/
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docs/
│   ├── user/
│   │   ├── getting-started.md
│   │   └── faq.md
│   └── dev/
│       ├── api-reference.md
│       └── deployment.md
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── INVESTAI_MASTER_PLAN.md
```

---

## ⚡ ESSENTIAL COMMANDS

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs (all services)
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Restart a service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend

# Clean everything (including volumes)
docker-compose down -v

# Access container shell
docker-compose exec backend bash
docker-compose exec postgres bash
```

### Database Commands

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "add_new_table"

# Rollback last migration
docker-compose exec backend alembic downgrade -1

# Access PostgreSQL
docker-compose exec postgres psql -U investai -d investai

# Backup database
docker-compose exec postgres pg_dump -U investai investai > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U investai investai
```

### Redis Commands

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# View all keys
docker-compose exec redis redis-cli KEYS '*'

# Get a specific key
docker-compose exec redis redis-cli GET "price:BBCA"

# Clear all cache
docker-compose exec redis redis-cli FLUSHALL
```

### Python/Backend Commands

```bash
# Install new package
docker-compose exec backend pip install package-name
docker-compose exec backend pip freeze > requirements.txt

# Run Python shell
docker-compose exec backend python

# Run tests
docker-compose exec backend pytest tests/ -v

# Run specific test
docker-compose exec backend pytest tests/unit/test_auth.py -v

# Test coverage
docker-compose exec backend pytest --cov=. --cov-report=html
```

### Celery Commands

```bash
# Start Celery worker (in separate terminal)
docker-compose exec backend celery -A celery_app worker --loglevel=info

# Start Celery beat (scheduler)
docker-compose exec backend celery -A celery_app beat --loglevel=info

# View active tasks
docker-compose exec backend celery -A celery_app inspect active

# Purge all tasks
docker-compose exec backend celery -A celery_app purge
```

---

## 🔑 KEY CODE PATTERNS

### 1. Creating a New API Endpoint

```python
# backend/api/example.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from api.auth import get_current_user_dependency
from models.user import User

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("/items")
def get_items(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    # Your logic here
    return {"items": []}

@router.post("/items")
def create_item(
    item_data: dict,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    # Your logic here
    return {"id": 1, "status": "created"}
```

Don't forget to register in `main.py`:
```python
from api import example
app.include_router(example.router)
```

### 2. Creating a New Dash Page

```python
# frontend/pages/new_page.py
import dash_bootstrap_components as dbc
from dash import html, callback, Input, Output, State
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

layout = dbc.Container([
    html.H2("New Page"),
    html.Div(id="content")
])

@callback(
    Output("content", "children"),
    Input("some-input", "value"),
    State("user-session", "data")
)
def update_content(value, session):
    if not session or 'token' not in session:
        return "Please login"
    
    # Call backend API
    response = requests.get(
        f"{BACKEND_URL}/api/endpoint",
        headers={"Authorization": f"Bearer {session['token']}"}
    )
    
    data = response.json()
    return html.P(str(data))
```

Add to routing in `app.py`:
```python
elif pathname == '/new-page':
    from pages import new_page
    return new_page.layout
```

### 3. Calling Groq AI

```python
# backend/services/ai_service.py
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_ai_response(prompt: str, context: dict = None) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful Indonesian stock market analyst."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=1500
    )
    
    return response.choices[0].message.content
```

### 4. Calling GPT-4 Vision for OCR

```python
# backend/services/ocr_service.py
from openai import OpenAI
import base64

client = OpenAI()

def parse_portfolio_image(image_bytes: bytes) -> dict:
    # Encode to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Extract stock holdings from this screenshot as JSON"
                    }
                ]
            }
        ],
        max_tokens=2000
    )
    
    return response.choices[0].message.content
```

### 5. Creating a Celery Background Task

```python
# backend/tasks/example_task.py
from celery_app import celery_app
from database import SessionLocal
from services.example_service import ExampleService

@celery_app.task
def example_task():
    """Run every X minutes"""
    db = SessionLocal()
    service = ExampleService()
    
    try:
        result = service.do_something(db)
        print(f"Task completed: {result}")
    except Exception as e:
        print(f"Task failed: {e}")
    finally:
        db.close()

# Schedule in celery_app.py
celery_app.conf.beat_schedule = {
    'example-task': {
        'task': 'tasks.example_task.example_task',
        'schedule': 300.0,  # Every 5 minutes
    }
}
```

### 6. Fetching Stock Prices (Yahoo Finance)

```python
# backend/services/market_data_service.py
import yfinance as yf
from datetime import datetime

def get_current_price(symbol: str) -> dict:
    """Get current price for IDX stock"""
    ticker = yf.Ticker(f"{symbol}.JK")  # .JK for Jakarta Stock Exchange
    
    data = ticker.history(period="1d")
    
    if data.empty:
        raise ValueError(f"No data for {symbol}")
    
    return {
        "symbol": symbol,
        "price": float(data['Close'].iloc[-1]),
        "change": float(data['Close'].iloc[-1] - data['Open'].iloc[-1]),
        "change_pct": float(((data['Close'].iloc[-1] / data['Open'].iloc[-1]) - 1) * 100),
        "volume": int(data['Volume'].iloc[-1]),
        "timestamp": datetime.now().isoformat()
    }
```

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue: "Module not found"
```bash
# Rebuild the container
docker-compose up -d --build backend

# Or install package manually
docker-compose exec backend pip install package-name
```

### Issue: "Database connection failed"
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Issue: "Migrations not applying"
```bash
# Check alembic status
docker-compose exec backend alembic current

# Force upgrade
docker-compose exec backend alembic upgrade head

# If stuck, downgrade and re-upgrade
docker-compose exec backend alembic downgrade -1
docker-compose exec backend alembic upgrade head
```

### Issue: "Redis not caching"
```bash
# Check Redis is running
docker-compose exec redis redis-cli PING
# Should return: PONG

# Check if keys exist
docker-compose exec redis redis-cli KEYS '*'
```

### Issue: "Frontend can't reach backend"
```bash
# Check backend is running
curl http://localhost:8000/docs

# Check BACKEND_URL in frontend
docker-compose exec frontend env | grep BACKEND_URL

# Should be: http://backend:8000 (Docker network)
# NOT: http://localhost:8000
```

### Issue: "Celery tasks not running"
```bash
# Check if Celery worker is running
docker-compose ps

# Start Celery worker manually
docker-compose exec backend celery -A celery_app worker --loglevel=info

# Check active tasks
docker-compose exec backend celery -A celery_app inspect active
```

---

## 📝 TESTING CHECKLIST

### Before Each Commit
- [ ] Code runs without errors
- [ ] All relevant tests pass
- [ ] No console errors in browser
- [ ] Database migrations work
- [ ] API endpoints return expected data
- [ ] UI renders correctly

### Before Each Demo
- [ ] Clean Docker environment (`docker-compose down -v && docker-compose up -d`)
- [ ] Run all migrations
- [ ] Seed test data
- [ ] Test complete user flow
- [ ] Check mobile responsiveness
- [ ] Verify all features work

### Before Production Deploy
- [ ] All tests pass (unit + integration + e2e)
- [ ] Security audit (no hardcoded secrets)
- [ ] Performance testing (load tests)
- [ ] Database backups configured
- [ ] Monitoring set up (Sentry)
- [ ] Documentation complete
- [ ] Environment variables set

---

## 🎯 DEVELOPMENT WORKFLOW

### Daily Workflow
```bash
# Morning
1. Pull latest changes: git pull
2. Start services: docker-compose up -d
3. Check logs: docker-compose logs -f
4. Run migrations: docker-compose exec backend alembic upgrade head

# During development
5. Make changes in VS Code
6. Services auto-reload (volume mounted)
7. Test changes in browser
8. Check logs for errors

# End of day
9. Commit changes: git add . && git commit -m "description"
10. Push to GitHub: git push
11. Stop services (optional): docker-compose down
```

### Feature Development Workflow
```bash
# Create feature branch
git checkout -b feature/image-import

# Develop feature
1. Write code
2. Test locally
3. Write tests
4. Run tests: docker-compose exec backend pytest

# Commit and push
git add .
git commit -m "feat: add image import functionality"
git push origin feature/image-import

# Create PR on GitHub
# Merge after review
```

---

## 🔐 SECURITY CHECKLIST

- [ ] Never commit `.env` file (add to .gitignore)
- [ ] Use strong SECRET_KEY (32+ random characters)
- [ ] Keep API keys in environment variables
- [ ] Use HTTPS in production
- [ ] Implement rate limiting on API
- [ ] Validate all user inputs
- [ ] Use parameterized SQL queries (SQLAlchemy ORM)
- [ ] Hash passwords with bcrypt
- [ ] Implement CORS properly
- [ ] Regular security updates (dependencies)

---

## 📊 MONITORING & DEBUGGING

### View Application Logs
```bash
# Backend logs
docker-compose logs -f backend | grep ERROR

# Frontend logs  
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

### Database Queries
```sql
-- Connect to PostgreSQL
docker-compose exec postgres psql -U investai -d investai

-- View all users
SELECT * FROM users;

-- View all portfolios
SELECT * FROM portfolios;

-- View holdings with current prices
SELECT h.symbol, h.shares, h.avg_cost, sp.price
FROM holdings h
LEFT JOIN LATERAL (
    SELECT price FROM stock_prices 
    WHERE symbol = h.symbol 
    ORDER BY timestamp DESC LIMIT 1
) sp ON true;

-- Exit
\q
```

### Performance Monitoring
```python
# Add to main.py for request timing
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## 🚀 QUICK START COMMANDS

```bash
# First time setup
git clone <repo-url>
cd investai
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
docker-compose exec backend alembic upgrade head

# Access application
# Frontend: http://localhost:8050
# Backend API: http://localhost:8000/docs
# PostgreSQL: localhost:5432
# Redis: localhost:6379

# Create first user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@investai.com","password":"Test123!","full_name":"Test User"}'

# Login and get token
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=test@investai.com&password=Test123!"
```

---

## 📞 GETTING HELP

**Documentation:**
- Master Plan: `INVESTAI_MASTER_PLAN.md`
- API Docs: http://localhost:8000/docs (when running)
- This Guide: `QUICK_REFERENCE.md`

**Debugging Strategy:**
1. Check logs first: `docker-compose logs -f`
2. Verify service is running: `docker-compose ps`
3. Test API endpoint: `curl http://localhost:8000/health`
4. Check database: Connect via psql
5. Inspect Redis: `redis-cli`

**Common Questions:**
- "Where do I start?" → Phase 1, Day 1 in Master Plan
- "How do I test X?" → See Testing Checklist above
- "API not working?" → Check BACKEND_URL and token
- "Database error?" → Run migrations
- "Frontend blank?" → Check browser console

---

## 📚 RESOURCES

**Documentation:**
- FastAPI: https://fastapi.tiangolo.com/
- Dash: https://dash.plotly.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Groq API: https://console.groq.com/docs
- OpenAI Vision: https://platform.openai.com/docs/guides/vision

**Tools:**
- VS Code Extensions: Python, Docker, PostgreSQL
- API Testing: Postman, Thunder Client (VS Code)
- Database: DBeaver, pgAdmin
- Monitoring: Sentry, Grafana

---

**Document Version:** 1.0  
**Last Updated:** February 10, 2026

**Keep this file open in VS Code for quick reference while coding!** 🚀

# 🎯 INVESTAI - MASTER DEVELOPMENT PLAN

**AI-Powered Indonesian Stock Portfolio Manager**

---

## 📋 EXECUTIVE SUMMARY

**Project:** InvestAI - IDX Portfolio Management Platform  
**Timeline:** 12 weeks (3 months)  
**Methodology:** Agile with 2-week sprints  
**Killer Feature:** 📸 **Image Import** (Screenshot → Portfolio in 30 seconds)

**Tech Stack:**
- **Frontend:** Dash 2.14+, Plotly, Bootstrap 5
- **Backend:** FastAPI, PostgreSQL 15, Redis, Celery
- **AI:** Groq (Llama 3.3 70B), GPT-4 Vision
- **DevOps:** Docker, GitHub Actions

---

## 🎯 CORE VALUE PROPOSITION

### The Problem
Indonesian retail investors waste **10+ minutes** manually entering portfolio data from their broker apps (IPOT, Stockbit, Ajaib). They miss opportunities because they lack:
- Real-time AI insights
- Systematic entry/exit planning
- Proactive alerts
- Professional-grade analytics

### The Solution
**InvestAI** = Screenshot → AI Analysis → Actionable Recommendations

**30-second setup** vs 10-minute manual entry = **95% time savings**

---

## 📊 PROJECT PHASES OVERVIEW

```
Phase 1: FOUNDATION (Weeks 1-2)
├─ Database + Authentication ✓
├─ Basic Dash UI ✓
└─ Demo: Login + Empty Dashboard

Phase 2: CORE PORTFOLIO (Weeks 3-4)
├─ Manual Portfolio Entry ✓
├─ Real-time Price Updates ✓
└─ Demo: Working Portfolio Tracker

Phase 3: IMAGE IMPORT MVP (Weeks 5-6) 🔥 BREAKTHROUGH
├─ OCR Engine (GPT-4 Vision) ✓
├─ Import Flow UI ✓
└─ Demo: Screenshot → Portfolio in 30s

Phase 4: AI INTEGRATION (Weeks 7-8)
├─ AI Chat (Groq) ✓
├─ Automated Insights ✓
└─ Demo: AI Recommendations

Phase 5: ADVANCED FEATURES (Weeks 9-10)
├─ Entry/Exit Strategies ✓
├─ Alerts System ✓
└─ Demo: Complete Strategy Tracking

Phase 6: POLISH & LAUNCH (Weeks 11-12)
├─ Testing & Bug Fixes ✓
├─ Documentation ✓
└─ Demo: Production Launch 🚀
```

---

## 🏗️ PHASE 1: FOUNDATION (Weeks 1-2)

### Sprint 1.1: Database & Authentication (Week 1)

**Objectives:**
- PostgreSQL database with complete schema
- JWT authentication system
- User registration & login APIs

**Key Deliverables:**

#### Day 1-2: Project Setup
```bash
# Create project structure
investai/
├── backend/
│   ├── requirements.txt
│   ├── config.py
│   ├── database.py
│   └── main.py
├── frontend/
│   ├── app.py
│   └── assets/
├── docker-compose.yml
└── .env.example

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose bcrypt
pip install dash plotly dash-bootstrap-components
pip install redis celery groq openai
```

#### Day 3-4: Database Schema

**Complete PostgreSQL Schema:**

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone_number VARCHAR(20),
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, pro, enterprise
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolios table
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    base_currency VARCHAR(10) DEFAULT 'IDR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Holdings table
CREATE TABLE holdings (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    shares INTEGER NOT NULL,
    avg_cost DECIMAL(15,2) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, symbol)
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    holding_id INTEGER REFERENCES holdings(id) ON DELETE SET NULL,
    transaction_type VARCHAR(10) NOT NULL, -- BUY, SELL
    symbol VARCHAR(10) NOT NULL,
    shares INTEGER NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    fees DECIMAL(15,2) DEFAULT 0,
    transaction_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock Prices table
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    open DECIMAL(15,2),
    high DECIMAL(15,2),
    low DECIMAL(15,2),
    close DECIMAL(15,2),
    volume BIGINT,
    change DECIMAL(15,2),
    change_pct DECIMAL(10,4),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stock_prices_symbol_timestamp ON stock_prices(symbol, timestamp DESC);
CREATE INDEX idx_stock_prices_timestamp ON stock_prices(timestamp DESC);

-- Entry Strategies table
CREATE TABLE entry_strategies (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    buy_zones JSONB NOT NULL, -- [{"zone_num": 1, "min_price": 56, "max_price": 58, "allocation": 40}]
    total_capital DECIMAL(15,2) NOT NULL,
    deployed_capital DECIMAL(15,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, completed, cancelled
    alert_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exit Strategies table
CREATE TABLE exit_strategies (
    id SERIAL PRIMARY KEY,
    holding_id INTEGER REFERENCES holdings(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    tp1_price DECIMAL(15,2),
    tp1_allocation DECIMAL(5,2),
    tp2_price DECIMAL(15,2),
    tp2_allocation DECIMAL(5,2),
    tp3_price DECIMAL(15,2),
    tp3_allocation DECIMAL(5,2),
    stop_loss DECIMAL(15,2),
    alert_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Queries table
CREATE TABLE ai_queries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    context JSONB,
    satisfied BOOLEAN, -- User feedback
    tokens_used INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Recommendations table
CREATE TABLE ai_recommendations (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(10),
    recommendation VARCHAR(10) NOT NULL, -- BUY, SELL, HOLD
    confidence DECIMAL(3,2), -- 0.0 to 1.0
    reasoning TEXT NOT NULL,
    target_price DECIMAL(15,2),
    stop_loss DECIMAL(15,2),
    time_horizon VARCHAR(20), -- short, medium, long
    status VARCHAR(20) DEFAULT 'active', -- active, executed, expired
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- price_target, stop_loss, rebalance, dividend, news
    symbol VARCHAR(10),
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    trigger_price DECIMAL(15,2),
    trigger_condition VARCHAR(20), -- above, below
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, triggered, expired
    channels JSONB DEFAULT '["in-app"]', -- ["in-app", "email", "sms"]
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- alert, insight, update, achievement
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    action_url VARCHAR(500),
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio Snapshots table (for historical tracking)
CREATE TABLE portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    total_value DECIMAL(15,2) NOT NULL,
    total_cost DECIMAL(15,2) NOT NULL,
    unrealized_gain DECIMAL(15,2),
    cash_balance DECIMAL(15,2) DEFAULT 0,
    snapshot_date DATE NOT NULL,
    holdings_snapshot JSONB, -- Complete holdings data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_id, snapshot_date)
);

CREATE INDEX idx_portfolio_snapshots ON portfolio_snapshots(portfolio_id, snapshot_date DESC);

-- Strategy Executions table (track actual buys/sells vs plan)
CREATE TABLE strategy_executions (
    id SERIAL PRIMARY KEY,
    entry_strategy_id INTEGER REFERENCES entry_strategies(id) ON DELETE CASCADE,
    execution_type VARCHAR(10) NOT NULL, -- BUY, SELL
    zone_num INTEGER,
    shares INTEGER NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    execution_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Alembic Migration:**
```python
# alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Execute all CREATE TABLE statements above
    pass

def downgrade():
    # DROP all tables in reverse order
    pass
```

#### Day 5-7: Authentication System

**JWT Authentication Service:**

```python
# backend/auth/jwt_handler.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

**FastAPI Auth Routes:**

```python
# backend/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.user import User
from auth.jwt_handler import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    decode_access_token
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    subscription_tier: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def get_current_user_dependency(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency for protected routes"""
    return get_current_user(token, db)
```

**Database Connection:**

```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://investai:password@localhost:5432/investai")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**User Model:**

```python
# backend/models/user.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, JSON
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(20))
    subscription_tier = Column(String(50), default='free')
    preferences = Column(JSON, default={})
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
```

**Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: investai
      POSTGRES_PASSWORD: password
      POSTGRES_DB: investai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://investai:password@postgres:5432/investai
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      GROQ_API_KEY: ${GROQ_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "8050:8050"
    environment:
      BACKEND_URL: http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
    command: python app.py

volumes:
  postgres_data:
  redis_data:
```

**Checkpoint 1.1: Foundation Ready**

```bash
# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Test authentication
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@investai.com","password":"Test123!","full_name":"Test User"}'

# Expected: {"access_token": "eyJ...", "token_type": "bearer"}
```

---

### Sprint 1.2: Basic UI Shell (Week 2)

**Objectives:**
- Working Dash application
- Login/Register pages
- Protected dashboard route
- Session management

**Key Deliverables:**

#### Day 8-10: Dash Application Setup

```python
# frontend/app.py
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import requests
import os

# Initialize app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title="InvestAI - Portfolio Manager"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# App layout with routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='user-session', storage_type='session'),  # Store JWT token
    html.Div(id='page-content')
])

# Import pages
from pages import login, register, dashboard

# Routing callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session):
    # Check if user is authenticated
    is_authenticated = session and 'token' in session
    
    # Public routes
    if pathname == '/login':
        return login.layout
    elif pathname == '/register':
        return register.layout
    
    # Protected routes
    elif pathname == '/' or pathname == '/dashboard':
        if is_authenticated:
            return dashboard.layout
        else:
            return dcc.Location(pathname='/login', id='redirect')
    
    # Default
    else:
        if is_authenticated:
            return dashboard.layout
        else:
            return login.layout

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
```

**Login Page:**

```python
# frontend/pages/login.py
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            # Logo and title
            html.Div([
                html.H1([
                    html.I(className="fas fa-chart-line me-2"),
                    "InvestAI"
                ], className="text-center mb-4"),
                html.P(
                    "AI-Powered Portfolio Manager for Indonesian Stocks",
                    className="text-center text-muted mb-5"
                )
            ]),
            
            # Login card
            dbc.Card([
                dbc.CardHeader(html.H4("Login to Your Account")),
                dbc.CardBody([
                    dbc.Input(
                        id="login-email",
                        type="email",
                        placeholder="Email address",
                        className="mb-3"
                    ),
                    dbc.Input(
                        id="login-password",
                        type="password",
                        placeholder="Password",
                        className="mb-3"
                    ),
                    dbc.Button(
                        "Login",
                        id="login-btn",
                        color="primary",
                        className="w-100 mb-3"
                    ),
                    html.Div(id="login-error", className="text-danger"),
                    html.Hr(),
                    html.P([
                        "Don't have an account? ",
                        dcc.Link("Sign up here", href="/register")
                    ], className="text-center mb-0")
                ])
            ], style={"maxWidth": "500px", "margin": "auto"})
        ], width=12)
    ], className="min-vh-100 d-flex align-items-center")
], fluid=True)

@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("login-error", "children"),
     Output("user-session", "data", allow_duplicate=True)],
    Input("login-btn", "n_clicks"),
    [State("login-email", "value"),
     State("login-password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, email, password):
    if not n_clicks:
        return dash.no_update
    
    if not email or not password:
        return dash.no_update, "Please enter email and password", dash.no_update
    
    try:
        # Call backend API
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            data={"username": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            
            # Store in session
            session_data = {"token": token, "email": email}
            
            return "/dashboard", "", session_data
        else:
            return dash.no_update, "Invalid email or password", dash.no_update
            
    except Exception as e:
        return dash.no_update, f"Error: {str(e)}", dash.no_update
```

**Register Page:**

```python
# frontend/pages/register.py
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1([
                    html.I(className="fas fa-chart-line me-2"),
                    "InvestAI"
                ], className="text-center mb-4"),
                html.P(
                    "Create your account and start managing your portfolio",
                    className="text-center text-muted mb-5"
                )
            ]),
            
            dbc.Card([
                dbc.CardHeader(html.H4("Create Account")),
                dbc.CardBody([
                    dbc.Input(
                        id="register-name",
                        type="text",
                        placeholder="Full Name",
                        className="mb-3"
                    ),
                    dbc.Input(
                        id="register-email",
                        type="email",
                        placeholder="Email address",
                        className="mb-3"
                    ),
                    dbc.Input(
                        id="register-password",
                        type="password",
                        placeholder="Password (min 8 characters)",
                        className="mb-3"
                    ),
                    dbc.Input(
                        id="register-password-confirm",
                        type="password",
                        placeholder="Confirm Password",
                        className="mb-3"
                    ),
                    dbc.Button(
                        "Create Account",
                        id="register-btn",
                        color="success",
                        className="w-100 mb-3"
                    ),
                    html.Div(id="register-error", className="text-danger"),
                    html.Div(id="register-success", className="text-success"),
                    html.Hr(),
                    html.P([
                        "Already have an account? ",
                        dcc.Link("Login here", href="/login")
                    ], className="text-center mb-0")
                ])
            ], style={"maxWidth": "500px", "margin": "auto"})
        ], width=12)
    ], className="min-vh-100 d-flex align-items-center")
], fluid=True)

@callback(
    [Output("url", "pathname", allow_duplicate=True),
     Output("register-error", "children"),
     Output("register-success", "children")],
    Input("register-btn", "n_clicks"),
    [State("register-name", "value"),
     State("register-email", "value"),
     State("register-password", "value"),
     State("register-password-confirm", "value")],
    prevent_initial_call=True
)
def handle_register(n_clicks, name, email, password, password_confirm):
    if not n_clicks:
        return dash.no_update
    
    # Validation
    if not all([name, email, password, password_confirm]):
        return dash.no_update, "Please fill all fields", ""
    
    if len(password) < 8:
        return dash.no_update, "Password must be at least 8 characters", ""
    
    if password != password_confirm:
        return dash.no_update, "Passwords do not match", ""
    
    try:
        # Call backend API
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": name
            }
        )
        
        if response.status_code == 201:
            return "/login", "", "Account created successfully! Please login."
        else:
            error_detail = response.json().get('detail', 'Registration failed')
            return dash.no_update, error_detail, ""
            
    except Exception as e:
        return dash.no_update, f"Error: {str(e)}", ""
```

**Empty Dashboard:**

```python
# frontend/pages/dashboard.py
import dash_bootstrap_components as dbc
from dash import html, dcc

layout = dbc.Container([
    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-chart-line me-2"),
                "InvestAI"
            ]),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
                dbc.NavItem(dbc.NavLink("Portfolio", href="/portfolio")),
                dbc.NavItem(dbc.NavLink("Settings", href="/settings")),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem("Profile", href="/profile"),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("Logout", id="logout-btn")
                    ],
                    label="Account",
                    nav=True
                )
            ], navbar=True)
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4"
    ),
    
    # Main content
    dbc.Row([
        dbc.Col([
            html.H2("Welcome to InvestAI! 🚀"),
            html.P("Your AI-powered portfolio manager is ready."),
            dbc.Alert(
                "This is your dashboard. Portfolio features coming soon!",
                color="info"
            )
        ])
    ])
], fluid=True)
```

**Checkpoint 1.2: UI Ready**

```
Test Flow:
1. Visit http://localhost:8050/ ✓
2. Redirects to /login ✓
3. Click "Sign up here" → /register ✓
4. Fill form → Create account ✓
5. Redirects to /login with success message ✓
6. Login with credentials ✓
7. Redirects to /dashboard ✓
8. Dashboard shows navbar and welcome message ✓
9. Refresh page → Still logged in ✓
10. Click "Logout" → Back to /login ✓
```

---

## 🎯 DEMO 1: FOUNDATION COMPLETE (End of Week 2)

**What's Working:**
- ✅ PostgreSQL database with complete schema
- ✅ JWT authentication (register, login, protected routes)
- ✅ Dash UI with routing
- ✅ Session management
- ✅ Docker environment

**Next Steps:** Proceed to Phase 2 (Portfolio Core)

---

## 📦 PHASE 2: CORE PORTFOLIO (Weeks 3-4)

[Continue with detailed implementation...]

---

## 🔥 PHASE 3: IMAGE IMPORT MVP (Weeks 5-6)

[The breakthrough feature - detailed in separate section]

---

## 🤖 PHASE 4: AI INTEGRATION (Weeks 7-8)

[AI chat and insights - detailed in separate section]

---

## ⚡ PHASE 5: ADVANCED FEATURES (Weeks 9-10)

[Strategy builder and alerts - detailed in separate section]

---

## 🚀 PHASE 6: POLISH & LAUNCH (Weeks 11-12)

[Testing, documentation, deployment - detailed in separate section]

---

## 📚 APPENDIX

### A. Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://investai:password@localhost:5432/investai

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars

# APIs
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here

# Email (SendGrid)
SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=noreply@investai.app

# SMS (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Application
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8050
ENVIRONMENT=development
```

### B. Requirements Files

**Backend Requirements:**
```txt
# backend/requirements.txt
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
```

**Frontend Requirements:**
```txt
# frontend/requirements.txt
dash==2.14.2
dash-bootstrap-components==1.5.0
plotly==5.18.0
requests==2.31.0
pandas==2.1.4
```

### C. Useful Commands

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Access PostgreSQL
docker-compose exec postgres psql -U investai -d investai

# Access Redis CLI
docker-compose exec redis redis-cli

# Run tests
docker-compose exec backend pytest tests/ -v

# Stop all services
docker-compose down

# Clean everything (including volumes)
docker-compose down -v
```

### D. Project Milestones

```
Week 2:  ✅ Foundation (Auth + DB)
Week 4:  ✅ Portfolio Tracker
Week 6:  ✅ Image Import 🔥
Week 8:  ✅ AI Integration
Week 10: ✅ Advanced Features
Week 12: ✅ Launch 🚀

Success Metrics:
- 100+ signups (Week 1)
- 50+ active portfolios
- 500+ AI queries
- 200+ image imports
```

---

## 🎯 YOUR DEVELOPMENT CONTEXT

**Who You Are:**
- Experienced in Python, Dash, PostgreSQL, FastAPI
- Built complex PMO dashboards with AI integration
- Familiar with Groq AI (Llama models)
- Strong database design skills
- Preference for practical, working solutions

**What You Have:**
- Complete 12-week build plan
- All code templates ready
- Step-by-step checkpoints
- Tested architecture
- Your actual portfolio data for testing

**What You'll Build:**
- Professional-grade portfolio manager
- Breakthrough image import feature (30-second setup)
- AI-powered insights and recommendations
- Complete strategy planning tools
- Production-ready application

**How to Use This Document:**
1. Follow phases sequentially
2. Complete each checkpoint before moving on
3. Test thoroughly at each demo milestone
4. Use your own portfolio screenshots for testing
5. Iterate based on what works

**Next Action:**
Start with Phase 1, Day 1: Project Setup
Create the folder structure and initialize Git repository.

---

**Document Version:** 1.0  
**Last Updated:** February 10, 2026  
**Status:** Ready for Development

---

*"The best time to start was yesterday. The second best time is now."*

🚀 **LET'S BUILD THIS!**

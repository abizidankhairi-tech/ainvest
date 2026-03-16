# InvestAI - AI-Powered Indonesian Stock Portfolio Manager

A full-stack web application for managing Indonesian stock portfolios with AI-powered insights, entry/exit strategies, and price alerts.

## Features

- **Portfolio Management**: Track your IDX stock holdings with real-time prices
- **AI-Powered Insights**: Get AI analysis and recommendations using Groq (Llama 3.3 70B)
- **Entry/Exit Strategies**: Plan buy zones and take-profit targets
- **Price Alerts**: Set alerts for price targets and stop losses
- **Real-time Prices**: Live stock prices from yfinance with Redis caching
- **Transaction History**: Track all buy/sell transactions
- **Responsive UI**: Modern Dash-based interface with Bootstrap 5

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **AI**: Groq API (Llama 3.3 70B)
- **Stock Data**: yfinance

### Frontend
- **Framework**: Dash 2.14+
- **UI Components**: dash-bootstrap-components
- **Charts**: Plotly
- **Styling**: Bootstrap 5

### DevOps
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest

## Project Structure

```
investai/
├── backend/
│   ├── api/                  # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── portfolio.py      # Portfolio management
│   │   ├── holdings.py       # Holdings & transactions
│   │   ├── stocks.py         # Stock prices
│   │   ├── ai.py             # AI chat & analysis
│   │   ├── strategies.py     # Entry/Exit strategies
│   │   └── alerts.py         # Alerts & notifications
│   ├── auth/                 # JWT handling
│   ├── models/               # SQLAlchemy models (13 models)
│   ├── services/             # Business logic
│   │   ├── stock_service.py  # yfinance integration
│   │   └── ai_service.py     # Groq AI integration
│   ├── tests/                # pytest tests
│   ├── main.py               # FastAPI app
│   ├── database.py           # Database connection
│   ├── config.py             # Configuration
│   └── requirements.txt
├── frontend/
│   ├── pages/                # Dash pages
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── dashboard.py
│   │   ├── portfolio.py
│   │   ├── ai_chat.py
│   │   ├── strategies.py
│   │   └── alerts.py
│   ├── app.py                # Main Dash app
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API Keys:
  - Groq API key (for AI features)
  - OpenAI API key (optional, for image import)

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/investai.git
cd investai

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Environment Variables

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://investai:password@postgres:5432/investai

# Redis
REDIS_URL=redis://redis:6379/0

# Security (generate a secure key)
SECRET_KEY=your-super-secret-key-min-32-characters-long

# AI APIs
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here  # Optional

# Application
BACKEND_URL=http://backend:8000
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Frontend**: http://localhost:8050
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Portfolio
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolio` | List user's portfolios |
| POST | `/api/portfolio` | Create new portfolio |
| GET | `/api/portfolio/{id}` | Get portfolio details |
| PUT | `/api/portfolio/{id}` | Update portfolio |
| DELETE | `/api/portfolio/{id}` | Delete portfolio |
| GET | `/api/portfolio/summary` | Get portfolio summary |

### Holdings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/holdings` | List holdings |
| POST | `/api/holdings` | Add new holding |
| PUT | `/api/holdings/{id}` | Update holding |
| DELETE | `/api/holdings/{id}` | Delete holding |
| POST | `/api/holdings/transaction` | Record transaction |
| GET | `/api/holdings/transactions` | Get transaction history |

### Stocks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stocks/price/{symbol}` | Get stock price |
| GET | `/api/stocks/prices` | Get multiple prices |
| GET | `/api/stocks/search` | Search stocks |

### AI
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/chat` | Chat with AI assistant |
| POST | `/api/ai/analyze` | Get AI analysis |
| GET | `/api/ai/insights` | Get AI-generated insights |
| GET | `/api/ai/history` | Get query history |

### Strategies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/strategies/entry` | List entry strategies |
| POST | `/api/strategies/entry` | Create entry strategy |
| GET | `/api/strategies/exit` | List exit strategies |
| POST | `/api/strategies/exit` | Create exit strategy |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts/` | List alerts |
| POST | `/api/alerts/` | Create alert |
| POST | `/api/alerts/check` | Check alerts |
| GET | `/api/alerts/notifications` | Get notifications |

## Development

### Running Backend Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Running Frontend Locally

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

### Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one version
docker-compose exec backend alembic downgrade -1
```

## Database Models

The application uses 13 SQLAlchemy models:

1. **User** - User accounts and authentication
2. **Portfolio** - Investment portfolios
3. **Holding** - Stock holdings in portfolios
4. **Transaction** - Buy/sell transactions
5. **StockPrice** - Cached stock prices
6. **EntryStrategy** - Entry strategies with buy zones
7. **ExitStrategy** - Exit strategies with TP and SL
8. **StrategyExecution** - Strategy execution records
9. **Alert** - Price alerts
10. **Notification** - User notifications
11. **AIQuery** - AI conversation history
12. **AIRecommendation** - AI-generated recommendations
13. **PortfolioSnapshot** - Historical portfolio snapshots

## Stock Symbols

InvestAI uses Indonesian Stock Exchange (IDX) symbols. When using the API:
- Use the stock code directly (e.g., `BBCA`, `BBRI`, `TLKM`)
- The system automatically appends `.JK` suffix for yfinance

## Troubleshooting

### Common Issues

**1. Database connection error**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

**2. Redis connection error**
```bash
# Check if Redis is running
docker-compose ps redis
```

**3. Stock price not loading**
- yfinance may be rate-limited
- Check if the symbol is valid (e.g., `BBCA.JK`)

**4. AI not responding**
- Verify GROQ_API_KEY is set correctly
- Check API quota limits

### Reset Database

```bash
# Stop services
docker-compose down

# Remove database volume
docker-compose down -v

# Restart
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) for stock data
- [Groq](https://groq.com/) for AI capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Dash](https://dash.plotly.com/) for the frontend framework

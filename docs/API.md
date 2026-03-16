# InvestAI API Documentation

## Overview

The InvestAI API is a RESTful API built with FastAPI. All endpoints (except auth) require JWT authentication.

**Base URL**: `http://localhost:8000`

**OpenAPI/Swagger UI**: `http://localhost:8000/docs`

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Register

```http
POST /api/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
}
```

**Response** (201):
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

**Response** (200):
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### Get Current User

```http
GET /api/auth/me
Authorization: Bearer <token>
```

**Response** (200):
```json
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "subscription_tier": "free"
}
```

---

## Portfolio

### List Portfolios

```http
GET /api/portfolio
Authorization: Bearer <token>
```

**Response** (200):
```json
[
    {
        "id": 1,
        "name": "My Portfolio",
        "description": "Indonesian stocks",
        "is_active": true,
        "created_at": "2026-03-01T10:00:00"
    }
]
```

### Create Portfolio

```http
POST /api/portfolio
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "My Portfolio",
    "description": "Indonesian stocks"
}
```

### Get Portfolio Summary

```http
GET /api/portfolio/summary
Authorization: Bearer <token>
```

**Response** (200):
```json
{
    "portfolio_id": 1,
    "total_value": 95000000,
    "total_cost": 90000000,
    "unrealized_gain": 5000000,
    "unrealized_gain_pct": 5.56,
    "holdings_count": 5
}
```

---

## Holdings

### List Holdings

```http
GET /api/holdings
Authorization: Bearer <token>
```

**Response** (200):
```json
[
    {
        "id": 1,
        "symbol": "BBCA",
        "shares": 100,
        "avg_cost": 9000,
        "sector": "Financials",
        "industry": "Banking",
        "current_price": 9500,
        "market_value": 950000,
        "unrealized_gain": 50000,
        "unrealized_gain_pct": 5.56
    }
]
```

### Add Holding

```http
POST /api/holdings
Authorization: Bearer <token>
Content-Type: application/json

{
    "symbol": "BBRI",
    "shares": 200,
    "avg_cost": 4500,
    "sector": "Financials",
    "industry": "Banking"
}
```

### Record Transaction

```http
POST /api/holdings/transaction
Authorization: Bearer <token>
Content-Type: application/json

{
    "symbol": "BBCA",
    "transaction_type": "BUY",
    "shares": 50,
    "price": 9200,
    "transaction_date": "2026-03-15",
    "notes": "Adding to position"
}
```

**transaction_type**: `BUY` or `SELL`

### Get Transaction History

```http
GET /api/holdings/transactions
Authorization: Bearer <token>
```

---

## Stocks

### Get Stock Price

```http
GET /api/stocks/price/BBCA
Authorization: Bearer <token>
```

**Response** (200):
```json
{
    "symbol": "BBCA",
    "price": 9500,
    "change": 100,
    "change_pct": 1.06,
    "open": 9400,
    "high": 9550,
    "low": 9380,
    "volume": 15000000,
    "timestamp": "2026-03-15T15:00:00"
}
```

### Get Multiple Prices

```http
GET /api/stocks/prices?symbols=BBCA,BBRI,TLKM
Authorization: Bearer <token>
```

---

## AI

### Chat with AI

```http
POST /api/ai/chat
Authorization: Bearer <token>
Content-Type: application/json

{
    "message": "What stocks should I consider buying?",
    "include_portfolio": true,
    "conversation_history": []
}
```

**Response** (200):
```json
{
    "response": "Based on your portfolio analysis...",
    "tokens_used": 150,
    "response_time_ms": 1200
}
```

### Get AI Analysis

```http
POST /api/ai/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
    "analysis_type": "portfolio"
}
```

**analysis_type options**:
- `portfolio` - Analyze entire portfolio
- `stock` - Analyze specific stock (requires `symbol`)
- `entry_strategy` - Generate entry strategy (requires `symbol` and `capital`)

### Get AI Insights

```http
GET /api/ai/insights
Authorization: Bearer <token>
```

**Response** (200):
```json
[
    {
        "type": "opportunity",
        "title": "BBCA Near Support",
        "description": "BBCA is trading near key support level..."
    }
]
```

---

## Strategies

### Create Entry Strategy

```http
POST /api/strategies/entry
Authorization: Bearer <token>
Content-Type: application/json

{
    "symbol": "BBRI",
    "total_capital": 10000000,
    "buy_zones": [
        {
            "zone_num": 1,
            "min_price": 4200,
            "max_price": 4400,
            "allocation": 40
        },
        {
            "zone_num": 2,
            "min_price": 4000,
            "max_price": 4199,
            "allocation": 35
        },
        {
            "zone_num": 3,
            "min_price": 3800,
            "max_price": 3999,
            "allocation": 25
        }
    ],
    "alert_enabled": true
}
```

**Note**: Allocations must sum to 100%

### Create Exit Strategy

```http
POST /api/strategies/exit
Authorization: Bearer <token>
Content-Type: application/json

{
    "holding_id": 1,
    "tp1_price": 10000,
    "tp1_allocation": 30,
    "tp2_price": 11000,
    "tp2_allocation": 40,
    "tp3_price": 12000,
    "tp3_allocation": 30,
    "stop_loss": 8000,
    "alert_enabled": true
}
```

### Record Strategy Execution

```http
POST /api/strategies/entry/{strategy_id}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
    "entry_strategy_id": 1,
    "execution_type": "BUY",
    "zone_num": 1,
    "shares": 500,
    "price": 4300,
    "execution_date": "2026-03-15",
    "notes": "First buy in zone 1"
}
```

---

## Alerts

### Create Alert

```http
POST /api/alerts/
Authorization: Bearer <token>
Content-Type: application/json

{
    "alert_type": "price_target",
    "symbol": "BBCA",
    "trigger_price": 10000,
    "trigger_condition": "above",
    "message": "BBCA reached target price",
    "channels": ["in-app"]
}
```

**alert_type options**: `price_target`, `stop_loss`, `price_above`, `price_below`

**trigger_condition options**: `above`, `below`

### Check Alerts

```http
POST /api/alerts/check
Authorization: Bearer <token>
```

**Response** (200):
```json
{
    "triggered": [
        {
            "id": 1,
            "symbol": "BBCA",
            "trigger_price": 10000,
            "current_price": 10050,
            "message": "BBCA reached target price"
        }
    ],
    "checked": 5
}
```

### Get Notifications

```http
GET /api/alerts/notifications
Authorization: Bearer <token>
```

### Mark All Notifications Read

```http
PUT /api/alerts/notifications/read-all
Authorization: Bearer <token>
```

---

## Error Responses

### 400 Bad Request
```json
{
    "detail": "Invalid request body"
}
```

### 401 Unauthorized
```json
{
    "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "invalid email address",
            "type": "value_error"
        }
    ]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding rate limiting for:
- AI endpoints (expensive API calls)
- Stock price endpoints (external API calls)

---

## WebSocket (Future)

Real-time price updates will be available via WebSocket:

```
ws://localhost:8000/ws/prices?symbols=BBCA,BBRI
```

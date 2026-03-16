from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import api_router
from database import engine, Base

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="InvestAI",
    description="AI-Powered Indonesian Stock Portfolio Manager",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "name": "InvestAI API",
        "version": "1.0.0",
        "description": "AI-Powered Indonesian Stock Portfolio Manager",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

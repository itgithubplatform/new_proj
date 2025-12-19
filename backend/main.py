"""TalentScout FastAPI Application"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, chat, candidates
from app.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__

)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Hiring Assistant for TalentScout",
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


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(candidates.router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TalentScout AI Hiring Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "api": settings.API_V1_PREFIX
    }


# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from app.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    try:
        # Check vector DB
        from app.services.vector_db_service import vector_db_service
        vector_db_service.get_collection_stats()
        vector_db_status = "healthy"
    except Exception as e:
        logger.error(f"Vector DB health check failed: {str(e)}")
        vector_db_status = "unhealthy"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" and vector_db_status == "healthy" else "degraded",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        database=db_status,
        vector_db=vector_db_status
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting TalentScout API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    # Initialize vector DB
    try:
        from app.services.vector_db_service import vector_db_service
        stats = vector_db_service.get_collection_stats()
        logger.info(f"Vector DB initialized: {stats}")
    except Exception as e:
        logger.error(f"Vector DB initialization failed: {str(e)}")
    
    logger.info("TalentScout API started successfully!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down TalentScout API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

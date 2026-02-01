from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from database import init_database, close_database, run_migrations, seed_default_bins
from routers import bins_router, alerts_router, export_router, analytics_router, set_broadcast_bin_update
from services import set_broadcast_alert
from websocket import websocket_endpoint, manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Inventory Dashboard API...")
    
    # Initialize database
    await init_database()
    await run_migrations()
    await seed_default_bins()
    
    # Set up WebSocket broadcast functions
    set_broadcast_bin_update(manager.broadcast_bin_update)
    set_broadcast_alert(manager.broadcast_alert)
    
    logger.info("🚀 Server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_database()
    logger.info("Server stopped")


# Create FastAPI application
app = FastAPI(
    title="Smart Bin Inventory Dashboard API",
    description="RESTful API for receiving bin data and managing inventory dashboard",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api-docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bins_router)
app.include_router(alerts_router)
app.include_router(export_router)
app.include_router(analytics_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "websocket_clients": manager.get_connection_count()
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_endpoint(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

"""FastAPI application for mock marketplace services."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from mock_services import (
    seller_metrics_router,
    search_ranking_router,
    pricing_router,
    fulfillment_router,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app for mock services
app = FastAPI(
    title="Marketplace Mock Services",
    description="Mock internal APIs simulating marketplace data services",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(seller_metrics_router)
app.include_router(search_ranking_router)
app.include_router(pricing_router)
app.include_router(fulfillment_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "Marketplace Mock Services",
        "version": "1.0.0",
        "services": [
            "Seller Metrics Service",
            "Search Ranking Service",
            "Pricing Service",
            "Fulfillment Service"
        ]
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "message": "All mock services operational"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Mock Services")
    uvicorn.run(
        "mock_services_app:app",
        host=settings.API_HOST,
        port=settings.MOCK_SERVICES_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

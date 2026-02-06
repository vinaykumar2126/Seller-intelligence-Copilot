"""Start all mock services on port 8001."""
import uvicorn
from fastapi import FastAPI
from mock_services import seller_metrics, search_ranking, pricing, fulfillment

app = FastAPI(title="Mock Marketplace Services")

# Include all mock service routers
app.include_router(seller_metrics.router)
app.include_router(search_ranking.router)
app.include_router(pricing.router)
app.include_router(fulfillment.router)

if __name__ == "__main__":
    print("🚀 Starting Mock Marketplace Services on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)


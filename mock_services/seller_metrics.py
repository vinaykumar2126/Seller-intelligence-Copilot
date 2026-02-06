"""Mock seller metrics service."""
import logging
from fastapi import APIRouter, HTTPException
from models.schemas import SellerMetrics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/seller-metrics", tags=["seller-metrics"])

# Mock data store
MOCK_METRICS = {
    "listing_001": SellerMetrics(
        listing_id="listing_001",
        impressions=5000,
        clicks=50,
        ctr=0.01,  # 1% CTR - low
        conversions=2,
        conversion_rate=0.04  # 4% conversion rate
    ),       
    "listing_002": SellerMetrics(
        listing_id="listing_002",
        impressions=15000,
        clicks=600,
        ctr=0.04,  # 4% CTR - healthy
        conversions=120,
        conversion_rate=0.20  # 20% conversion rate - excellent
    ),
    "listing_003": SellerMetrics(
        listing_id="listing_003",
        impressions=200,
        clicks=10,
        ctr=0.05,  # 5% CTR - good
        conversions=0,
        conversion_rate=0.0  # No conversions
    ),
}


@router.get("/metrics/{listing_id}", response_model=SellerMetrics)
async def get_seller_metrics(listing_id: str):
    """
    Retrieve seller metrics for a listing.
    
    Returns:
        - impressions: Number of times the listing was viewed
        - clicks: Number of clicks on the listing
        - ctr: Click-through rate
        - conversions: Number of successful purchases
        - conversion_rate: Conversion rate
    """
    logger.info(f"Fetching seller metrics for listing: {listing_id}")
    
    if listing_id not in MOCK_METRICS:
        logger.warning(f"Listing {listing_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Listing '{listing_id}' not found. Available test listings: listing_001, listing_002, listing_003, 12345"
        )
    
    return MOCK_METRICS[listing_id]

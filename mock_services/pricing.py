"""Mock pricing service."""
import logging
from fastapi import APIRouter
from models.schemas import PricingData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["pricing"])

# Mock data store
MOCK_PRICING = {
    "listing_001": PricingData(
        listing_id="listing_001",
        seller_price=299.99,
        median_competitor_price=249.99,
        price_percentile=85.0,  # Expensive compared to competitors
        currency="USD",
        price_difference_percent=20.0  # 20% more expensive
    ),
    "listing_002": PricingData(
        listing_id="listing_002",
        seller_price=49.99,
        median_competitor_price=52.99,
        price_percentile=35.0,  # Competitively priced
        currency="USD",
        price_difference_percent=-5.66  # 5.66% cheaper
    ),
    "listing_003": PricingData(
        listing_id="listing_003",
        seller_price=15.99,
        median_competitor_price=12.99,
        price_percentile=75.0,  # Somewhat expensive
        currency="USD",
        price_difference_percent=23.1  # 23.1% more expensive
    ),
}


@router.get("/pricing/{listing_id}", response_model=PricingData)
async def get_pricing_data(listing_id: str):
    """
    Retrieve pricing comparison data for a listing.
    
    Returns:
        - seller_price: Seller's current price
        - median_competitor_price: Median price among competitors
        - price_percentile: Where seller's price falls (0-100)
        - currency: Currency code
        - price_difference_percent: Percentage difference from median
    """
    logger.info(f"Fetching pricing data for listing: {listing_id}")
    
    if listing_id not in MOCK_PRICING:
        logger.warning(f"Listing {listing_id} not found, returning default pricing")
        return PricingData(
            listing_id=listing_id,
            seller_price=50.00,
            median_competitor_price=50.00,
            price_percentile=50.0,
            currency="USD",
            price_difference_percent=0.0
        )
    
    return MOCK_PRICING[listing_id]

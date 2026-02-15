"""Mock fulfillment service."""
import logging
from fastapi import APIRouter
from models.schemas import FulfillmentData

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fulfillment", tags=["fulfillment"])

# Mock data store
MOCK_FULFILLMENT = {
    "listing_001": FulfillmentData(
        listing_id="listing_001",
        shipping_days=12,  # Slow shipping
        return_policy="30-day return, buyer pays shipping",
        in_stock=True,
        fulfillment_method="FBM"  # Fulfilled by Merchant
    ),
    "listing_002": FulfillmentData(
        listing_id="listing_002",
        shipping_days=2,  # Fast shipping
        return_policy="Free 30-day return",
        in_stock=True,
        fulfillment_method="FBA"  # Fulfilled by Amazon
    ),
    "listing_003": FulfillmentData(
        listing_id="listing_003",
        shipping_days=5,  # Moderate shipping
        return_policy="15-day return, buyer pays shipping",
        in_stock=False,  # Out of stock!
        fulfillment_method="FBM"
    ),
}


@router.get("/fulfillment/{listing_id}", response_model=FulfillmentData)
async def get_fulfillment_data(listing_id: str):
    """
    Retrieve fulfillment and shipping data for a listing.
    
    Returns:
        - shipping_days: Estimated shipping time in days
        - return_policy: Return policy description
        - in_stock: Whether item is in stock
        - fulfillment_method: Fulfillment method (FBA/FBM)
    """
    logger.info(f"Fetching fulfillment data for listing: {listing_id}")
    
    if listing_id not in MOCK_FULFILLMENT:
        logger.warning(f"Listing {listing_id} not found, returning default fulfillment")
        return FulfillmentData(
            listing_id=listing_id,
            shipping_days=5,
            return_policy="30-day return",
            in_stock=True,
            fulfillment_method="FBM"
        )
    print(f"Returning fulfillment data for listing {listing_id}: {MOCK_FULFILLMENT[listing_id]}")  # Debug statement
    return MOCK_FULFILLMENT[listing_id]

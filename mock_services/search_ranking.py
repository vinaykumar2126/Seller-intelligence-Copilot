"""Mock search ranking service."""
import logging
from fastapi import APIRouter
from models.schemas import SearchRanking

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search-ranking", tags=["search-ranking"])

# Mock data store
MOCK_RANKINGS = {
    "listing_001": SearchRanking(
        listing_id="listing_001",
        avg_rank=45.5,  # Poor ranking
        page_number=5,  # Page 5
        keyword_match_score=0.3,  # Poor keyword optimization
        category="Electronics"
    ),
    "listing_002": SearchRanking(
        listing_id="listing_002",
        avg_rank=3.2,  # Excellent ranking
        page_number=1,
        keyword_match_score=0.92,  # Excellent keyword optimization
        category="Home & Kitchen"
    ),
    "listing_003": SearchRanking(
        listing_id="listing_003",
        avg_rank=15.0,  # Moderate ranking
        page_number=2,
        keyword_match_score=0.65,  # Moderate keyword optimization
        category="Books"
    ),
}


@router.get("/ranking/{listing_id}", response_model=SearchRanking)
async def get_search_ranking(listing_id: str):
    """
    Retrieve search ranking data for a listing.
    
    Returns:
        - avg_rank: Average position in search results
        - page_number: Typical page number where listing appears
        - keyword_match_score: Quality of keyword match (0-1)
        - category: Product category
    """
    logger.info(f"Fetching search ranking for listing: {listing_id}")
    
    if listing_id not in MOCK_RANKINGS:
        logger.warning(f"Listing {listing_id} not found, returning default ranking")
        return SearchRanking(
            listing_id=listing_id,
            avg_rank=20.0,
            page_number=2,
            keyword_match_score=0.5,
            category="General"
        )
    
    return MOCK_RANKINGS[listing_id]

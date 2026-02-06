"""MCP tool implementations for each marketplace service."""
import logging
from typing import Any, Dict, List
from .base import MCPToolBase

logger = logging.getLogger(__name__)


class SellerMetricsTool(MCPToolBase):
    """Tool to fetch seller metrics (impressions, clicks, CTR, conversions)."""
    
    @property
    def name(self) -> str:
        return "get_seller_metrics"
    
    @property
    def description(self) -> str:
        return (
            "Retrieves performance metrics for a listing including impressions, "
            "clicks, click-through rate (CTR), conversions, and conversion rate. "
            "Use this to understand if the listing is getting visibility and engagement."
        )
    
    def _build_url(self, listing_id: str) -> str:
        return f"{self.base_url}/seller-metrics/metrics/{listing_id}"
    
    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed insights to the response."""
        normalized = data.copy()
        
        # Add interpretations
        if normalized.get("ctr", 0) < 0.02:
            normalized["ctr_interpretation"] = "low"
        elif normalized.get("ctr", 0) < 0.05:
            normalized["ctr_interpretation"] = "moderate"
        else:
            normalized["ctr_interpretation"] = "good"
        
        if normalized.get("conversion_rate", 0) < 0.05:
            normalized["conversion_interpretation"] = "low"
        elif normalized.get("conversion_rate", 0) < 0.15:
            normalized["conversion_interpretation"] = "moderate"
        else:
            normalized["conversion_interpretation"] = "good"
        
        return normalized


class SearchRankingTool(MCPToolBase):
    """Tool to fetch search ranking data."""
    
    @property
    def name(self) -> str:
        return "get_search_ranking"
    
    @property
    def description(self) -> str:
        return (
            "Retrieves search ranking information including average rank position, "
            "page number, and keyword match score. Use this to understand discoverability "
            "and SEO optimization."
        )
    
    def _build_url(self, listing_id: str) -> str:
        return f"{self.base_url}/search-ranking/ranking/{listing_id}"
    
    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed insights to the response."""
        normalized = data.copy()
        
        # Add interpretations
        avg_rank = normalized.get("avg_rank", 999)
        if avg_rank <= 10:
            normalized["visibility"] = "excellent"
        elif avg_rank <= 20:
            normalized["visibility"] = "good"
        elif avg_rank <= 50:
            normalized["visibility"] = "poor"
        else:
            normalized["visibility"] = "very_poor"
        
        keyword_score = normalized.get("keyword_match_score", 0)
        if keyword_score >= 0.8:
            normalized["seo_quality"] = "excellent"
        elif keyword_score >= 0.6:
            normalized["seo_quality"] = "good"
        elif keyword_score >= 0.4:
            normalized["seo_quality"] = "needs_improvement"
        else:
            normalized["seo_quality"] = "poor"
        
        return normalized


class PricingTool(MCPToolBase):
    """Tool to fetch pricing comparison data."""
    
    @property
    def name(self) -> str:
        return "get_pricing_data"
    
    @property
    def description(self) -> str:
        return (
            "Retrieves pricing information including seller's price, median competitor price, "
            "price percentile, and price difference percentage. Use this to understand "
            "competitive positioning and pricing strategy."
        )
    
    def _build_url(self, listing_id: str) -> str:
        return f"{self.base_url}/pricing/pricing/{listing_id}"
    
    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed insights to the response."""
        normalized = data.copy()
        
        # Add interpretations
        percentile = normalized.get("price_percentile", 50)
        if percentile >= 75:
            normalized["price_competitiveness"] = "expensive"
        elif percentile >= 60:
            normalized["price_competitiveness"] = "above_average"
        elif percentile >= 40:
            normalized["price_competitiveness"] = "competitive"
        elif percentile >= 25:
            normalized["price_competitiveness"] = "below_average"
        else:
            normalized["price_competitiveness"] = "very_competitive"
        
        return normalized


class FulfillmentTool(MCPToolBase):
    """Tool to fetch fulfillment and shipping data."""
    
    @property
    def name(self) -> str:
        return "get_fulfillment_data"
    
    @property
    def description(self) -> str:
        return (
            "Retrieves fulfillment information including shipping days, return policy, "
            "stock status, and fulfillment method. Use this to understand delivery "
            "competitiveness and availability issues."
        )
    
    def _build_url(self, listing_id: str) -> str:
        return f"{self.base_url}/fulfillment/fulfillment/{listing_id}"
    
    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add computed insights to the response."""
        normalized = data.copy()
        
        # Add interpretations
        shipping_days = normalized.get("shipping_days", 999)
        if shipping_days <= 2:
            normalized["shipping_speed"] = "fast"
        elif shipping_days <= 5:
            normalized["shipping_speed"] = "moderate"
        elif shipping_days <= 10:
            normalized["shipping_speed"] = "slow"
        else:
            normalized["shipping_speed"] = "very_slow"
        
        # Critical issue flag
        if not normalized.get("in_stock", True):
            normalized["critical_issue"] = "out_of_stock"
        
        return normalized


# Tool registry
def get_all_tools() -> List[MCPToolBase]:
    """
    Get all available MCP tools.
    
    Returns:
        List of instantiated tool objects
    """
    return [
        SellerMetricsTool(),
        SearchRankingTool(),
        PricingTool(),
        FulfillmentTool(),
    ]


def get_tool_by_name(tool_name: str) -> MCPToolBase:
    """
    Get a specific tool by name.
    
    Args:
        tool_name: Name of the tool to retrieve
        
    Returns:
        The tool instance
        
    Raises:
        ValueError: If tool not found
    """
    tools = {tool.name: tool for tool in get_all_tools()}
    
    if tool_name not in tools:
        raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(tools.keys())}")
    
    return tools[tool_name]

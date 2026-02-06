"""Pydantic models and schemas for the Seller Intelligence Copilot."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# ==================== Request/Response Models ====================

class AnalyzeRequest(BaseModel):
    """Request model for the analyze endpoint."""
    listing_id: str = Field(..., description="Unique identifier for the product listing")
    question: str = Field(..., description="Seller's question about their listing")


class AnalyzeResponse(BaseModel):
    """Response model for the analyze endpoint."""
    listing_id: str
    diagnosis: str = Field(..., description="Clear explanation of why the item isn't selling")
    recommendations: List[str] = Field(..., description="Actionable bullet-point recommendations")
    tools_used: List[str] = Field(..., description="List of tools/services consulted")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


# ==================== Mock Service Response Models ====================

class SellerMetrics(BaseModel):
    """Seller metrics data."""
    listing_id: str
    impressions: int = Field(..., description="Number of times the listing was viewed")
    clicks: int = Field(..., description="Number of clicks on the listing")
    ctr: float = Field(..., description="Click-through rate (clicks/impressions)")
    conversions: int = Field(..., description="Number of successful purchases")
    conversion_rate: float = Field(..., description="Conversion rate (conversions/clicks)")


class SearchRanking(BaseModel):
    """Search ranking data."""
    listing_id: str
    avg_rank: float = Field(..., description="Average position in search results")
    page_number: int = Field(..., description="Typical page number where listing appears")
    keyword_match_score: float = Field(..., ge=0, le=1, description="Quality of keyword match (0-1)")
    category: str = Field(..., description="Product category")


class PricingData(BaseModel):
    """Pricing comparison data."""
    listing_id: str
    seller_price: float = Field(..., description="Seller's current price")
    median_competitor_price: float = Field(..., description="Median price among competitors")
    price_percentile: float = Field(..., ge=0, le=100, description="Price percentile (0-100)")
    currency: str = Field(default="USD", description="Currency code")
    price_difference_percent: float = Field(..., description="Percentage difference from median")


class FulfillmentData(BaseModel):
    """Fulfillment and shipping data."""
    listing_id: str
    shipping_days: int = Field(..., description="Estimated shipping time in days")
    return_policy: str = Field(..., description="Return policy description")
    in_stock: bool = Field(..., description="Whether item is in stock")
    fulfillment_method: str = Field(..., description="Fulfillment method (e.g., FBA, FBM)")


# ==================== MCP Tool Models ====================

class MCPToolInput(BaseModel):
    """Base input model for MCP tools."""
    listing_id: str


class MCPToolOutput(BaseModel):
    """Base output model for MCP tools."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SellerMetricsToolOutput(MCPToolOutput):
    """Output from seller metrics tool."""
    data: Optional[SellerMetrics] = None


class SearchRankingToolOutput(MCPToolOutput):
    """Output from search ranking tool."""
    data: Optional[SearchRanking] = None


class PricingToolOutput(MCPToolOutput):
    """Output from pricing tool."""
    data: Optional[PricingData] = None


class FulfillmentToolOutput(MCPToolOutput):
    """Output from fulfillment tool."""
    data: Optional[FulfillmentData] = None


# ==================== Agent Models ====================

class ToolCall(BaseModel):
    """Represents a tool call decision."""
    tool_name: str
    reason: str
    listing_id: str


class AgentState(BaseModel):
    """Represents the agent's state during execution."""
    listing_id: str
    question: str
    tools_to_call: List[str] = Field(default_factory=list)
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    diagnosis: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    error: Optional[str] = None

"""Base class for MCP tools."""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import settings

logger = logging.getLogger(__name__)


class MCPToolBase(ABC):
    """
    Base class for all MCP tools.
    
    Each tool:
    - Is read-only
    - Has strict input/output schema
    - Calls a corresponding mock API
    - Normalizes responses before returning
    - Handles errors gracefully
    """
    
    def __init__(self, base_url: str = None):
        """Initialize the MCP tool with a base URL."""
        self.base_url = base_url or f"{settings.MOCK_SERVICES_HOST}:{settings.MOCK_SERVICES_PORT}"
        self.timeout = settings.SERVICE_TIMEOUT
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for identification."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for LLM context."""
        pass
    
    @abstractmethod
    def _build_url(self, listing_id: str) -> str:
        """Build the API endpoint URL."""
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.TimeoutException),
        reraise=True
    )
    async def _make_request(self, url: str) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    async def execute(self, listing_id: str) -> Dict[str, Any]:
        """
        Execute the tool and return normalized results.
        
        Args:
            listing_id: The listing ID to query
            
        Returns:
            Dictionary with 'success', 'data', and optional 'error' keys
        """
        try:
            logger.info(f"Executing {self.name} for listing {listing_id}")
            url = self._build_url(listing_id)
            data = await self._make_request(url)
            
            # Normalize the response
            normalized_data = self._normalize_response(data)
            
            logger.info(f"{self.name} executed successfully for listing {listing_id}")
            return {
                "success": True,
                "data": normalized_data,
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"{self.name} HTTP error for listing {listing_id}: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
            
        except httpx.TimeoutException as e:
            logger.error(f"{self.name} timeout for listing {listing_id}: {e}")
            return {
                "success": False,
                "data": None,
                "error": "Request timeout - service unavailable"
            }
            
        except Exception as e:
            logger.error(f"{self.name} unexpected error for listing {listing_id}: {e}", exc_info=True)
            return {
                "success": False,
                "data": None,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize the API response.
        Can be overridden by subclasses for custom normalization.
        """
        return data
    
    def to_llm_description(self) -> Dict[str, Any]:
        """
        Return tool description in a format suitable for LLM.
        Used by the agent to describe available tools to the LLM.
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "listing_id": {
                        "type": "string",
                        "description": "The listing ID to query"
                    }
                },
                "required": ["listing_id"]
            }
        }

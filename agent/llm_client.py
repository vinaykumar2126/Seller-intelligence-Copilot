"""LLM client for Ollama integration."""
import logging
import json
from typing import List, Dict, Any, Optional
import ollama
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for interacting with Ollama LLM.
    
    The LLM is used ONLY for:
    1. Deciding which tools to call based on the user's question
    2. Analyzing collected data and generating insights
    3. Producing seller-friendly recommendations
    
    The LLM NEVER fetches data directly or hallucinates information.
    """
    
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = None
    ):
        """Initialize Ollama client."""
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT
        
        # Configure ollama client
        ollama.Client(host=self.base_url)
        
        logger.info(f"Initialized Ollama client with model: {self.model}")
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def decide_tools(
        self,
        question: str,
        available_tools: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Decide which tools to call based on the user's question.
        
        Args:
            question: The seller's question
            available_tools: List of available tools with descriptions
            
        Returns:
            List of tool names to call
        """
        try:
            # Build the prompt
            tools_description = "\n".join([
                f"- {tool['name']}: {tool['description']}"
                for tool in available_tools
            ])
            
            prompt = f"""You are an assistant helping to analyze e-commerce product listings.

Available tools:
{tools_description}

User's question: "{question}"

Based on the question, which tools should we call to gather the necessary data?
Return ONLY a JSON array of tool names, nothing else. For example: ["get_seller_metrics", "get_pricing_data"]

If the question is general or asks "why is my product not selling", call ALL tools.
If the question is specific (e.g., about pricing), call only relevant tools.

Response (JSON array only):"""

            logger.info(f"Requesting tool selection from LLM for question: {question}")
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.1,  # Low temperature for consistent tool selection
                }
            )
            
            # Parse response
            content = response['message']['content'].strip()
            
            # Try to extract JSON array
            # Handle cases where LLM might wrap in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            tool_names = json.loads(content)
            
            logger.info(f"LLM selected tools: {tool_names}")
            return tool_names
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM tool selection response: {e}")
            logger.error(f"Raw response: {content}")
            # Fallback: call all tools
            return [tool['name'] for tool in available_tools]
            
        except Exception as e:
            logger.error(f"Error in tool selection: {e}", exc_info=True)
            # Fallback: call all tools
            return [tool['name'] for tool in available_tools]
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def analyze_and_recommend(
        self,
        question: str,
        tool_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the collected data and generate recommendations.
        
        Args:
            question: The seller's original question
            tool_results: Results from all tool executions
            
        Returns:
            Dictionary with 'diagnosis' and 'recommendations' keys
        """
        try:
            # Build the prompt with all data
            data_summary = json.dumps(tool_results, indent=2)
            
            prompt = f"""You are an expert e-commerce consultant analyzing why a product isn't selling well.

Seller's question: "{question}"

Data collected from marketplace systems:
{data_summary}

Based on this REAL data (do not make up any numbers), provide:

1. DIAGNOSIS: A clear, 2-3 sentence explanation of the main issues preventing sales. Be specific and cite the actual numbers from the data.

2. RECOMMENDATIONS: 3-5 actionable bullet points the seller can implement immediately. Each should be specific and based on the data.

Format your response as JSON:
{{
  "diagnosis": "Your diagnosis here...",
  "recommendations": [
    "First recommendation...",
    "Second recommendation...",
    "Third recommendation..."
  ]
}}

Important:
- Only reference data that was provided
- Be specific with numbers (e.g., "Your CTR is 1%, which is below the 3% benchmark")
- Use business-friendly language
- Focus on actionable items
- Prioritize the most impactful issues

Response (JSON only):"""

            logger.info("Requesting analysis from LLM")
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.3,  # Some creativity for recommendations
                }
            )
            
            # Parse response
            content = response['message']['content'].strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            logger.info("LLM analysis completed successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM analysis response: {e}")
            logger.error(f"Raw response: {content}")
            # Fallback response
            return {
                "diagnosis": "Unable to generate detailed analysis due to parsing error. Please review the data manually.",
                "recommendations": [
                    "Review your listing's performance metrics",
                    "Compare your pricing with competitors",
                    "Optimize your product keywords and title"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}", exc_info=True)
            raise
    
    def check_availability(self) -> bool:
        """
        Check if Ollama is available and the model is accessible.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            # Try to list models
            models = ollama.list()
            model_names = [m['name'] for m in models.get('models', [])]
            
            # Check if our model is available
            if self.model not in model_names and f"{self.model}:latest" not in model_names:
                logger.warning(f"Model {self.model} not found. Available models: {model_names}")
                return False
            
            logger.info(f"Ollama is available with model: {self.model}")
            return True
            
        except Exception as e:
            logger.error(f"Ollama availability check failed: {e}")
            return False

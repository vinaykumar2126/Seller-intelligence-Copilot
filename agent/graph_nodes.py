"""LangGraph node implementations - agents as graph nodes."""
import logging
from typing import Dict, Any
import asyncio

from .graph_state import AgentState
from .llm_client import OllamaClient
from mcp_tools import get_all_tools, get_tool_by_name

logger = logging.getLogger(__name__)


class LangGraphNodes:
    """
    Collection of LangGraph nodes (agents).
    
    Each method is a node in the graph that:
    - Receives the current state
    - Performs its task
    - Returns updates to merge into state
    """
    
    def __init__(self, llm_client: OllamaClient = None):
        """Initialize with LLM client."""
        self.llm_client = llm_client or OllamaClient()
        self.available_tools = get_all_tools()
        logger.info(f"✨ LangGraph nodes initialized with {len(self.available_tools)} tools")
    
    async def tool_selector_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Node 1: Tool Selection
        
        Decides which tools to call based on the question.
        """
        logger.info("🎯 [ToolSelector] Starting...")
        
        question = state["question"]
        
        # Get tool descriptions
        tool_descriptions = [tool.to_llm_description() for tool in self.available_tools]
        
        # Use LLM to select tools
        tool_names = await self.llm_client.decide_tools(
            question=question,
            available_tools=tool_descriptions
        )
        
        # Validate tool names
        valid_tool_names = [tool.name for tool in self.available_tools]
        selected_tools = [name for name in tool_names if name in valid_tool_names]
        
        if not selected_tools:
            logger.warning("⚠️  No valid tools selected, using all tools")
            selected_tools = valid_tool_names
        
        logger.info(f"✅ [ToolSelector] Selected {len(selected_tools)} tools")
        
        return {
            "selected_tools": selected_tools,
            "current_stage": 1,
            "stages_completed": ["tool_selection"]
        }
    
    async def data_collector_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Node 2: Data Collection
        
        Executes selected tools in parallel and gathers data.
        """
        logger.info("📡 [DataCollector] Starting...")
        
        listing_id = state["listing_id"]
        selected_tools = state.get("selected_tools", [])
        
        if not selected_tools:
            logger.error("❌ No tools selected")
            return {
                "tool_results": {},
                "successful_count": 0,
                "total_tools": 0,
                "errors": ["No tools were selected"]
            }
        
        logger.info(f"📡 Executing {len(selected_tools)} tools in parallel")
        
        # Create tasks for parallel execution
        tasks = []
        tool_names = []
        
        for tool_name in selected_tools:
            try:
                tool = get_tool_by_name(tool_name)
                task = tool.execute(listing_id)
                tasks.append(task)
                tool_names.append(tool_name)
            except ValueError as e:
                logger.error(f"❌ Tool not found: {e}")
                continue
        
        # Execute all tools in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        tool_results = {}
        successful_count = 0
        errors = []
        
        for tool_name, result in zip(tool_names, results):
            if isinstance(result, Exception):
                logger.error(f"❌ {tool_name} failed: {result}")
                tool_results[tool_name] = {
                    "success": False,
                    "error": str(result)
                }
                errors.append(f"{tool_name}: {str(result)}")
            else:
                tool_results[tool_name] = result
                if result.get("success"):
                    successful_count += 1
                    logger.info(f"✅ {tool_name} completed")
        
        logger.info(f"📊 Data collection complete: {successful_count}/{len(tool_names)} successful")
        
        return {
            "tool_results": tool_results,
            "successful_count": successful_count,
            "total_tools": len(tool_names),
            "current_stage": 2,
            "stages_completed": ["data_collection"],
            "errors": errors if errors else []
        }
    
    async def analyst_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Node 3: Analysis
        
        Analyzes collected data and generates diagnosis.
        """
        logger.info("🔬 [Analyst] Starting...")
        
        question = state["question"]
        tool_results = state.get("tool_results", {})
        
        # Filter successful results
        successful_results = {
            tool_name: result.get("data")
            for tool_name, result in tool_results.items()
            if result.get("success", False) and result.get("data")
        }
        
        if not successful_results:
            logger.error("❌ No successful data to analyze")
            return {
                "diagnosis": "Unable to analyze - no data available from marketplace services.",
                "key_insights": [],
                "errors": ["No successful tool results to analyze"]
            }
        
        logger.info(f"📈 Analyzing data from {len(successful_results)} sources")
        
        # Get LLM analysis
        analysis = await self.llm_client.analyze_and_recommend(
            question=question,
            tool_results=successful_results
        )
        
        # Extract key insights
        key_insights = self._extract_insights(successful_results)
        
        logger.info(f"💡 Generated diagnosis with {len(key_insights)} key insights")
        
        return {
            "diagnosis": analysis.get("diagnosis", "Analysis unavailable"),
            "key_insights": key_insights,
            "current_stage": 3,
            "stages_completed": ["analysis"]
        }
    
    async def recommender_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Node 4: Recommendations
        
        Generates prioritized, actionable recommendations.
        """
        logger.info("💡 [Recommender] Starting...")
        
        question = state["question"]
        tool_results = state.get("tool_results", {})
        key_insights = state.get("key_insights", [])
        
        # Filter successful results
        successful_results = {
            tool_name: result.get("data")
            for tool_name, result in tool_results.items()
            if result.get("success", False) and result.get("data")
        }
        
        if not successful_results:
            return {
                "recommendations": ["Contact support - unable to generate recommendations"],
                "priority_level": "high",
                "errors": ["No data available for recommendations"]
            }
        
        # Get recommendations from LLM
        analysis = await self.llm_client.analyze_and_recommend(
            question=question,
            tool_results=successful_results
        )
        
        recommendations = analysis.get("recommendations", [])
        
        # Determine priority
        priority_level = self._determine_priority(key_insights, successful_results)
        
        logger.info(f"📝 Generated {len(recommendations)} recommendations (Priority: {priority_level})")
        
        return {
            "recommendations": recommendations,
            "priority_level": priority_level,
            "current_stage": 4,
            "stages_completed": ["recommendations"]
        }
    
    def _extract_insights(self, data: Dict[str, Any]) -> list[str]:
        """Extract key insights from the data."""
        insights = []
        
        # Check metrics
        if "get_seller_metrics" in data:
            metrics = data["get_seller_metrics"]
            if metrics.get("ctr_interpretation") == "low":
                insights.append(f"Low CTR: {metrics.get('ctr', 0)*100:.1f}%")
            if metrics.get("conversion_interpretation") == "low":
                insights.append(f"Low conversion rate: {metrics.get('conversion_rate', 0)*100:.1f}%")
        
        # Check ranking
        if "get_search_ranking" in data:
            ranking = data["get_search_ranking"]
            if ranking.get("visibility") in ["poor", "very_poor"]:
                insights.append(f"Poor visibility: Rank {ranking.get('avg_rank')}")
            if ranking.get("seo_quality") in ["needs_improvement", "poor"]:
                insights.append(f"SEO needs work: Score {ranking.get('keyword_match_score')}")
        
        # Check pricing
        if "get_pricing_data" in data:
            pricing = data["get_pricing_data"]
            if pricing.get("price_competitiveness") == "expensive":
                insights.append(f"Overpriced: {pricing.get('price_difference_percent'):.1f}% above median")
        
        # Check fulfillment
        if "get_fulfillment_data" in data:
            fulfillment = data["get_fulfillment_data"]
            if fulfillment.get("shipping_speed") in ["slow", "very_slow"]:
                insights.append(f"Slow shipping: {fulfillment.get('shipping_days')} days")
            if fulfillment.get("critical_issue"):
                insights.append(f"🚨 CRITICAL: {fulfillment.get('critical_issue')}")
        
        return insights
    
    def _determine_priority(self, insights: list[str], data: Dict[str, Any]) -> str:
        """Determine priority level based on issues found."""
        # Critical issues
        if any("CRITICAL" in insight for insight in insights):
            return "critical"
        
        # Check for out of stock
        if "get_fulfillment_data" in data:
            if not data["get_fulfillment_data"].get("in_stock", True):
                return "critical"
        
        # High priority: multiple significant issues
        if len(insights) >= 3:
            return "high"
        
        # Medium priority: some issues
        if len(insights) >= 1:
            return "medium"
        
        # Low priority: minor optimizations
        return "low"

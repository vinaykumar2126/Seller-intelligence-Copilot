"""LangGraph-based crew orchestrator for Seller Intelligence."""
import logging
import time
from typing import Dict, Any, Annotated
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from .graph_state import AgentState
from .graph_nodes import LangGraphNodes
from .llm_client import OllamaClient

logger = logging.getLogger(__name__)


class AgentCrew:
    """
    LangGraph-based orchestrator for multi-agent workflow.
    
    This crew coordinates 4 specialized agents using LangGraph:
    1. ToolSelector - Decides which tools to use
    2. DataCollector - Gathers data from tools
    3. Analyst - Analyzes the data
    4. Recommender - Generates actionable recommendations
    
    The workflow is defined as a state graph with nodes and edges.
    """
    
    def __init__(self):
        """Initialize the LangGraph crew."""
        logger.info("🚀 Initializing LangGraph Agent Crew...")
        
        # Initialize nodes with LLM client
        self.nodes = LangGraphNodes(llm_client=OllamaClient())
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info("✨ LangGraph crew ready")
    
    def _build_graph(self) -> CompiledStateGraph:
        """
        Build the LangGraph state graph.
        
        Returns:
            Compiled state graph ready for execution
        """
        logger.info("🔧 Building LangGraph workflow...")
        
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("tool_selector", self.nodes.tool_selector_node)
        workflow.add_node("data_collector", self.nodes.data_collector_node)
        workflow.add_node("analyst", self.nodes.analyst_node)
        workflow.add_node("recommender", self.nodes.recommender_node)
        
        # Define edges (workflow)
        workflow.add_edge(START, "tool_selector")
        workflow.add_edge("tool_selector", "data_collector")
        workflow.add_edge("data_collector", "analyst")
        workflow.add_edge("analyst", "recommender")
        workflow.add_edge("recommender", END)
        
        # Compile the graph
        compiled_graph = workflow.compile()
        
        logger.info("✅ LangGraph workflow compiled")
        return compiled_graph
    
    async def analyze(self, listing_id: str, question: str) -> Dict[str, Any]:
        """
        Execute the LangGraph crew workflow.
        
        Args:
            listing_id: The product listing to analyze
            question: The seller's question/concern
            
        Returns:
            Complete analysis with all agent outputs
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🎬 STARTING LANGGRAPH WORKFLOW for Listing: {listing_id}")
        logger.info(f"❓ Question: {question}")
        logger.info(f"{'='*80}\n")
        
        start_time = time.time()
        
        # Initialize state
        initial_state: AgentState = {
            "listing_id": listing_id,
            "question": question,
            "selected_tools": [],
            "tool_results": {},
            "diagnosis": "",
            "key_insights": [],
            "recommendations": [],
            "priority_level": "medium",
            "errors": [],
            "stages_completed": [],
            "current_stage": 0,
            "successful_count": 0,
            "total_tools": 0
        }
        
        try:
            # Execute the graph
            logger.info("🚀 Invoking LangGraph...")
            final_state = await self.graph.ainvoke(initial_state)
            
            total_duration = time.time() - start_time
            
            # Log summary
            logger.info(f"\n{'='*80}")
            logger.info(f"🏁 LANGGRAPH WORKFLOW COMPLETE")
            logger.info(f"⏱️  Total time: {total_duration:.2f}s")
            logger.info(f"📊 Tools used: {len(final_state.get('selected_tools', []))}")
            logger.info(f"✅ Successful: {final_state.get('successful_count', 0)}/{final_state.get('total_tools', 0)}")
            logger.info(f"💡 Insights: {len(final_state.get('key_insights', []))}")
            logger.info(f"📝 Recommendations: {len(final_state.get('recommendations', []))}")
            logger.info(f"🎯 Priority: {final_state.get('priority_level', 'unknown')}")
            logger.info(f"{'='*80}\n")
            
            # Return structured response
            return {
                "listing_id": final_state["listing_id"],
                "diagnosis": final_state.get("diagnosis", ""),
                "recommendations": final_state.get("recommendations", []),
                "tools_used": final_state.get("selected_tools", []),
                "metadata": {
                    "question": final_state["question"],
                    "tool_results": final_state.get("tool_results", {}),
                    "key_insights": final_state.get("key_insights", []),
                    "priority_level": final_state.get("priority_level", "medium"),
                    "execution_time": total_duration,
                    "successful_count": final_state.get("successful_count", 0),
                    "total_tools": final_state.get("total_tools", 0),
                    "errors": final_state.get("errors", []),
                    "stages_completed": final_state.get("stages_completed", [])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ LangGraph workflow failed: {e}")
            total_duration = time.time() - start_time
            
            return {
                "listing_id": listing_id,
                "diagnosis": f"Workflow failed: {str(e)}",
                "recommendations": ["Contact support - workflow error"],
                "tools_used": [],
                "metadata": {
                    "question": question,
                    "tool_results": {},
                    "key_insights": [],
                    "priority_level": "critical",
                    "execution_time": total_duration,
                    "successful_count": 0,
                    "total_tools": 0,
                    "errors": [str(e)],
                    "stages_completed": []
                }
            }
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get current status of the LangGraph crew."""
        return {
            "framework": "LangGraph",
            "graph_nodes": ["tool_selector", "data_collector", "analyst", "recommender"],
            "workflow_type": "sequential",
            "status": "ready"
        }
    
    def get_workflow_diagram(self) -> list[Dict[str, str]]:
        """Get a visual representation of the LangGraph workflow."""
        return [
            {
                "stage": 1,
                "node": "tool_selector",
                "input": "question",
                "output": "selected_tools",
                "description": "Decides which marketplace tools to call"
            },
            {
                "stage": 2,
                "node": "data_collector",
                "input": "selected_tools + listing_id",
                "output": "tool_results",
                "description": "Executes tools in parallel and gathers data"
            },
            {
                "stage": 3,
                "node": "analyst",
                "input": "tool_results + question",
                "output": "diagnosis + key_insights",
                "description": "Analyzes data and identifies issues"
            },
            {
                "stage": 4,
                "node": "recommender",
                "input": "diagnosis + key_insights",
                "output": "recommendations + priority",
                "description": "Generates actionable recommendations"
            }
        ]

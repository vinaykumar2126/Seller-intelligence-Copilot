"""LangGraph state schema for the agent crew."""
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from datetime import datetime
import operator


class AgentState(TypedDict):
    """
    State that flows through the LangGraph workflow.
    
    LangGraph manages this state and passes it between nodes (agents).
    Each agent can read from and write to this shared state.
    """
    # Input
    listing_id: str
    question: str
    
    # Stage 1: Tool Selection
    selected_tools: Annotated[List[str], operator.add]
    
    # Stage 2: Data Collection
    tool_results: Dict[str, Any]
    successful_count: int
    total_tools: int
    
    # Stage 3: Analysis
    diagnosis: str
    key_insights: Annotated[List[str], operator.add]
    
    # Stage 4: Recommendations
    recommendations: Annotated[List[str], operator.add]
    priority_level: str
    
    # Metadata
    start_time: datetime
    errors: Annotated[List[str], operator.add]
    
    # Execution tracking
    current_stage: int
    stages_completed: Annotated[List[str], operator.add]

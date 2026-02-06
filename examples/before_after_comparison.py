"""
Example showing the difference between single-agent and crew approaches.
This demonstrates why the crew pattern is better organized.
"""

# =============================================================================
# BEFORE: Single-Agent Approach (orchestrator.py)
# =============================================================================

class SellerIntelligenceAgent:
    """One agent doing everything."""
    
    async def analyze(self, listing_id: str, question: str):
        # STEP 1: Tool selection (mixed with orchestration logic)
        tool_descriptions = [tool.to_llm_description() for tool in self.tools]
        tool_names = await self.llm_client.decide_tools(question, tool_descriptions)
        
        # STEP 2: Data collection (mixed in the same method)
        tasks = []
        for tool_name in tool_names:
            tool = get_tool_by_name(tool_name)
            tasks.append(tool.execute(listing_id))
        results = await asyncio.gather(*tasks)
        
        # STEP 3 & 4: Analysis and recommendations (combined)
        analysis = await self.llm_client.analyze_and_recommend(question, results)
        
        # Hard to track progress, hard to test independently
        return AnalyzeResponse(
            diagnosis=analysis["diagnosis"],
            recommendations=analysis["recommendations"]
        )


# =============================================================================
# AFTER: Multi-Agent Crew Approach
# =============================================================================

class ToolSelectorAgent(BaseAgent):
    """ONLY responsible for tool selection."""
    
    async def execute(self, context: Dict[str, Any]):
        question = context["question"]
        tool_descriptions = [tool.to_llm_description() for tool in self.tools]
        tool_names = await self.llm_client.decide_tools(question, tool_descriptions)
        
        self.logger.info(f"🎯 Selected {len(tool_names)} tools")
        
        return {
            "selected_tools": tool_names
        }


class DataCollectorAgent(BaseAgent):
    """ONLY responsible for data collection."""
    
    async def execute(self, context: Dict[str, Any]):
        listing_id = context["listing_id"]
        selected_tools = context["selected_tools"]
        
        tasks = []
        for tool_name in selected_tools:
            tool = get_tool_by_name(tool_name)
            tasks.append(tool.execute(listing_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info(f"📡 Collected data from {len(results)} sources")
        
        return {
            "tool_results": dict(zip(selected_tools, results))
        }


class AnalystAgent(BaseAgent):
    """ONLY responsible for analysis."""
    
    async def execute(self, context: Dict[str, Any]):
        question = context["question"]
        tool_results = context["tool_results"]
        
        analysis = await self.llm_client.analyze(question, tool_results)
        key_insights = self._extract_insights(tool_results)
        
        self.logger.info(f"🔬 Generated diagnosis with {len(key_insights)} insights")
        
        return {
            "diagnosis": analysis["diagnosis"],
            "key_insights": key_insights
        }


class RecommenderAgent(BaseAgent):
    """ONLY responsible for recommendations."""
    
    async def execute(self, context: Dict[str, Any]):
        tool_results = context["tool_results"]
        key_insights = context["key_insights"]
        
        recommendations = await self.llm_client.recommend(tool_results)
        priority = self._determine_priority(key_insights)
        
        self.logger.info(f"💡 Generated {len(recommendations)} recommendations")
        
        return {
            "recommendations": recommendations,
            "priority_level": priority
        }


class AgentCrew:
    """Coordinates all agents."""
    
    def __init__(self):
        self.crew = [
            ToolSelectorAgent(),
            DataCollectorAgent(),
            AnalystAgent(),
            RecommenderAgent()
        ]
    
    async def analyze(self, listing_id: str, question: str):
        context = {"listing_id": listing_id, "question": question}
        
        # Execute each agent in sequence
        for i, agent in enumerate(self.crew, 1):
            logger.info(f"STAGE {i}/{len(self.crew)}: {agent.name}")
            result = await agent.run(context)
            context.update(result)  # Pass results to next agent
        
        # Build final response
        return AnalyzeResponse(
            diagnosis=context["diagnosis"],
            recommendations=context["recommendations"],
            metadata={"crew_execution_log": self.execution_log}
        )


# =============================================================================
# COMPARISON
# =============================================================================

"""
TESTABILITY
-----------
Before: Must test entire workflow
    response = await agent.analyze("listing_001", "Why no sales?")
    # Hard to test individual pieces

After: Test each agent independently
    selector = ToolSelectorAgent()
    result = await selector.execute({"question": "Why no sales?"})
    assert "get_seller_metrics" in result["selected_tools"]


DEBUGGING
---------
Before: One log stream, hard to find issues
    INFO - Analysis started
    INFO - Executing tools
    ERROR - Something failed  # Which part failed?

After: Clear stage identification
    STAGE 1/4: ToolSelector
    ✅ ToolSelector completed in 2.14s
    
    STAGE 2/4: DataCollector
    ❌ DataCollector failed: Connection timeout  # Exact stage!


EXTENSIBILITY
-------------
Before: Modify one large class
    class SellerIntelligenceAgent:
        async def analyze(...):
            # Add new feature here? Where exactly?
            # Risk breaking existing logic

After: Add a new agent
    class ImageAnalysisAgent(BaseAgent):
        async def execute(self, context):
            # Your new feature
            pass
    
    # Just insert it in the workflow
    crew.crew.insert(2, ImageAnalysisAgent())


TRACKING
--------
Before: Limited visibility
    {
      "tools_used": ["get_seller_metrics", ...]
    }

After: Full execution log
    {
      "crew_execution_log": [
        {"stage": 1, "agent": "ToolSelector", "duration": 2.14},
        {"stage": 2, "agent": "DataCollector", "duration": 1.03},
        {"stage": 3, "agent": "Analyst", "duration": 3.21},
        {"stage": 4, "agent": "Recommender", "duration": 2.87}
      ],
      "total_duration_seconds": 9.25
    }


CODE ORGANIZATION
-----------------
Before: 213 lines in one file
    orchestrator.py (213 lines)
    - Tool selection logic
    - Data collection logic
    - Analysis logic
    - Recommendation logic
    - All mixed together

After: Separated by responsibility
    base_agent.py (90 lines)      - Abstract base
    crew_agents.py (300 lines)    - 4 specialized agents
    crew_orchestrator.py (260 lines) - Coordinator
    
    Each file has ONE clear purpose!


SINGLE RESPONSIBILITY PRINCIPLE
--------------------------------
Before: SellerIntelligenceAgent does EVERYTHING
    - Decides which tools to use ✓
    - Collects data ✓
    - Analyzes data ✓
    - Generates recommendations ✓
    - Tracks execution ✓
    - Handles errors ✓
    (Violates SRP!)

After: Each agent does ONE thing
    - ToolSelectorAgent: Decides which tools → That's it!
    - DataCollectorAgent: Collects data → That's it!
    - AnalystAgent: Analyzes data → That's it!
    - RecommenderAgent: Generates recommendations → That's it!
    - AgentCrew: Coordinates → That's it!
    (Follows SRP!)
"""

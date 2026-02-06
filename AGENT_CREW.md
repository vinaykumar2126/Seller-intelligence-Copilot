# Multi-Agent Crew Architecture

## 🎭 Overview

The Seller Intelligence Copilot has been redesigned using a **multi-agent crew pattern** where specialized agents work together in a coordinated workflow. This architecture provides better organization, tracking, and flexibility compared to a monolithic single-agent approach.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AgentCrew                               │
│                    (Crew Orchestrator)                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────┐
        │  Sequential Workflow (4 Stages)     │
        └─────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│ 🎯 Stage 1    │           │ 📡 Stage 2    │
│ ToolSelector  │─────────▶│ DataCollector │
│               │           │               │
│ Decides which │           │ Executes tools│
│ tools to use  │           │ in parallel   │
└───────────────┘           └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │ 🔬 Stage 3    │
                            │ Analyst       │
                            │               │
                            │ Analyzes data │
                            │ & finds issues│
                            └───────┬───────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │ 💡 Stage 4    │
                            │ Recommender   │
                            │               │
                            │ Generates     │
                            │ actions       │
                            └───────────────┘
```

## 👥 Agent Crew Members

### 1. **ToolSelectorAgent** 🎯
- **Role:** Tool Selection
- **Responsibility:** Analyzes the seller's question and decides which data sources are needed
- **Input:** `question`
- **Output:** `selected_tools`
- **LLM Usage:** Yes (decides which tools to call)

**Example:**
```python
# Question: "Why is my product not selling?"
# Output: ["get_seller_metrics", "get_search_ranking", 
#          "get_pricing_data", "get_fulfillment_data"]

# Question: "Is my pricing competitive?"
# Output: ["get_pricing_data", "get_seller_metrics"]
```

### 2. **DataCollectorAgent** 📡
- **Role:** Data Collection
- **Responsibility:** Executes selected tools in parallel and gathers marketplace data
- **Input:** `listing_id`, `selected_tools`
- **Output:** `tool_results`, `successful_count`
- **LLM Usage:** No (pure data fetching)

**Features:**
- Parallel execution for performance
- Automatic retry with exponential backoff
- Graceful error handling
- Success/failure tracking

### 3. **AnalystAgent** 🔬
- **Role:** Data Analysis
- **Responsibility:** Analyzes collected data and generates diagnosis
- **Input:** `question`, `tool_results`
- **Output:** `diagnosis`, `key_insights`
- **LLM Usage:** Yes (analyzes data and identifies issues)

**Capabilities:**
- Identifies performance issues
- Extracts key insights
- Generates human-readable diagnosis
- References actual data (no hallucinations)

### 4. **RecommenderAgent** 💡
- **Role:** Recommendation Generation
- **Responsibility:** Creates prioritized, actionable recommendations
- **Input:** `tool_results`, `key_insights`
- **Output:** `recommendations`, `priority_level`
- **LLM Usage:** Yes (generates recommendations)

**Priority Levels:**
- **Critical:** Out of stock, severe blocking issues
- **High:** Multiple significant problems
- **Medium:** Some issues requiring attention
- **Low:** Minor optimizations

## 🔄 Workflow Sequence

```
1. REQUEST RECEIVED
   ├─ listing_id: "listing_001"
   └─ question: "Why is my product not selling?"

2. STAGE 1: ToolSelector
   ├─ Analyzes question
   ├─ Selects: [get_seller_metrics, get_search_ranking, 
   │            get_pricing_data, get_fulfillment_data]
   └─ Duration: ~2s

3. STAGE 2: DataCollector
   ├─ Executes 4 tools in parallel
   ├─ Collects: metrics, ranking, pricing, fulfillment data
   ├─ Success: 4/4 tools
   └─ Duration: ~1s (parallel execution)

4. STAGE 3: Analyst
   ├─ Analyzes collected data
   ├─ Identifies: low CTR, high price, poor ranking
   ├─ Generates diagnosis
   └─ Duration: ~3s

5. STAGE 4: Recommender
   ├─ Creates 5 actionable recommendations
   ├─ Priority: HIGH
   └─ Duration: ~3s

6. RESPONSE SENT
   ├─ diagnosis: "Your product faces three main issues..."
   ├─ recommendations: [...]
   ├─ Total duration: ~9s
   └─ Crew execution log included
```

## 📊 Benefits of Crew Architecture

### 1. **Clear Separation of Concerns**
Each agent has one well-defined responsibility:
- No overlapping functionality
- Easy to understand what each agent does
- Reduced complexity

### 2. **Easy Progress Tracking**
You can see exactly where execution is at any time:
```python
# Check crew status
GET /crew/status

{
  "crew": {
    "agents": [
      {"name": "ToolSelector", "status": "completed"},
      {"name": "DataCollector", "status": "working"},
      {"name": "Analyst", "status": "idle"},
      {"name": "Recommender", "status": "idle"}
    ]
  }
}
```

### 3. **Independent Testing**
Each agent can be tested in isolation:
```python
# Test just the ToolSelector
selector = ToolSelectorAgent(llm_client)
result = await selector.execute({
    "question": "Is my price too high?"
})
assert "get_pricing_data" in result["selected_tools"]
```

### 4. **Flexible & Extensible**
Easy to add new agents or modify existing ones:
```python
# Add a new agent to the crew
class CompetitorAnalysisAgent(BaseAgent):
    async def execute(self, context):
        # Analyze competitor strategies
        pass

# Insert it anywhere in the workflow
crew.crew.insert(3, CompetitorAnalysisAgent())
```

### 5. **Better Logging & Debugging**
Each agent logs its activities:
```
🎬 CREW ANALYSIS STARTED
════════════════════════════════════════════════════════════════════════════════
STAGE 1/4: ToolSelector (tool_selector)
────────────────────────────────────────────────────────────────────────────────
🚀 ToolSelector starting execution...
📋 Analyzing question: 'Why is my product not selling?'
🎯 Selected 4 tools: ['get_seller_metrics', ...]
✅ ToolSelector completed in 2.14s

STAGE 2/4: DataCollector (data_collector)
────────────────────────────────────────────────────────────────────────────────
🚀 DataCollector starting execution...
🔍 Collecting data for listing listing_001
📡 Executing 4 tools in parallel
✅ get_seller_metrics completed
✅ get_search_ranking completed
✅ get_pricing_data completed
✅ get_fulfillment_data completed
📊 Data collection complete: 4/4 successful
✅ DataCollector completed in 1.03s
...
```

## 🎯 Code Organization

```
agent/
├── __init__.py              # Package exports
├── base_agent.py            # BaseAgent abstract class
├── crew_agents.py           # Specialized agent implementations
├── crew_orchestrator.py     # AgentCrew coordinator
├── llm_client.py            # Ollama LLM client
└── orchestrator.py          # Legacy single-agent (deprecated)
```

## 📝 Usage Examples

### Basic Usage
```python
from agent import AgentCrew

# Initialize the crew
crew = AgentCrew()

# Analyze a listing
response = await crew.analyze(
    listing_id="listing_001",
    question="Why is my product not selling?"
)

print(response.diagnosis)
print(response.recommendations)
```

### Get Crew Status
```python
# Check current status
status = crew.get_crew_status()
print(f"Crew size: {status['crew_size']}")
for agent_status in status['agents']:
    print(f"{agent_status['name']}: {agent_status['status']}")
```

### Get Execution Summary
```python
# After an analysis
summary = crew.get_execution_summary()
print(f"Total duration: {summary['total_duration_seconds']}s")
print(f"Stages completed: {summary['stages_completed']}")
for stage in summary['stages']:
    print(f"  {stage['agent']}: {stage['duration_seconds']:.2f}s")
```

### Health Check
```python
health = await crew.health_check()
print(f"Crew: {health['crew']}")
print(f"LLM: {health['llm']}")
for agent in health['agents']:
    print(f"  {agent['name']}: {'✅' if agent['ready'] else '❌'}")
```


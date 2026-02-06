# Seller Intelligence Copilot

An AI-powered assistant for e-commerce sellers that explains why products aren't selling and provides actionable recommendations.

## 🎯 Overview

This prototype demonstrates a production-style architecture for an e-commerce intelligence system that uses an LLM as a reasoning layer on top of real marketplace data. The system follows a strict separation of concerns where:

- **LLM never fetches data directly** - all data access goes through MCP tools
- **No hallucinations** - the LLM only reasons about real data
- **Modular architecture** - each component is independently testable and replaceable

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Main API (FastAPI)                      │
│                    POST /analyze endpoint                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Agent Orchestrator                         │
│  • Decides which tools to call (via LLM)                    │
│  • Executes tools in parallel                               │
│  • Passes results to LLM for analysis                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────┐
│        MCP Tool Layer              │
│  ┌──────────────────────────────┐  │
│  │ SellerMetricsTool            │  │
│  │ SearchRankingTool            │  │
│  │ PricingTool                  │  │
│  │ FulfillmentTool              │  │
│  └──────────────────────────────┘  │
└────────────┬───────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    Mock Marketplace Services        │
│  • Seller Metrics API               │
│  • Search Ranking API               │
│  • Pricing API                      │
│  • Fulfillment API                  │
└─────────────────────────────────────┘
```

## 📦 Project Structure

```
Seller-Intelligence-Copilot/
├── main.py                      # Main API application
├── mock_services_app.py         # Mock services application
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
│
├── models/
│   ├── __init__.py
│   └── schemas.py               # Pydantic models
│
├── mock_services/
│   ├── __init__.py
│   ├── seller_metrics.py        # Mock seller metrics service
│   ├── search_ranking.py        # Mock search ranking service
│   ├── pricing.py               # Mock pricing service
│   └── fulfillment.py           # Mock fulfillment service
│
├── mcp_tools/
│   ├── __init__.py
│   ├── base.py                  # Base MCP tool class
│   └── tools.py                 # Tool implementations
│
├── agent/
│   ├── __init__.py
│   ├── crew_orchestrator.py    # AgentCrew coordinator
│   ├── llm_client.py            # Ollama LLM client
│   └── graph_state.py           # Defines the agent shared state          
│   └── graph_nodes.py           # Collection of LangGraph nodes i.e CREW AI
├── AGENT_CREW.md                # Crew architecture documentation
└── TEST_DATA.md                 # Test data reference
```

## 🚀 Getting Started

### Prerequisites

1. **Python 3.9+**
2. **Ollama** (self-hosted LLM)
   ```bash
   # Install Ollama (macOS)
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull a model (e.g., llama3.2)
   ollama pull llama3.2
   
   # Verify it's running
   ollama list
   ```

### Installation

1. **Clone and navigate to the directory:**
   ```bash
   cd Seller-Intelligence-Copilot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env if you need to change defaults
   ```

### Running the Application

You need to run **two separate servers**:

#### 1. Mock Services (Terminal 1)
```bash
python mock_services_app.py
```
This starts the mock marketplace services at `http://localhost:8001`

#### 2. Main API (Terminal 2)
```bash
python main.py
```
This starts the main Copilot API at `http://localhost:8000`

### Verify Setup

1. **Check Ollama:**
   ```bash
   curl http://localhost:11434/api/version
   ```

2. **Check Mock Services:**
   ```bash
   curl http://localhost:8001/health
   ```

3. **Check Main API:**
   ```bash
   curl http://localhost:8000/health
   ```

## 📝 API Usage

### Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

### New Crew Endpoints

```bash
# Get crew status and workflow
curl http://localhost:8000/crew/status

# View workflow diagram
curl http://localhost:8000/crew/workflow
```

### Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "listing_001",...",
  "recommendations": [
    "Optimize your product title and main image - your low CTR of 1%...",
    "Reduce your price to $249.99 or lower to match competitor pricing...",
    "Improve your search ranking by optimizing keywords...",
    "Consider switching to faster fulfillment...",
    "Review and enhance your product description..."
  ],
  "tools_used": [
    "get_seller_metrics",
    "get_search_ranking",
    "get_pricing_data",
    "get_fulfillment_data"
  ],
  "metadata": {
    "question": "Why is my product not selling?",
    "key_insights": [
      "Low CTR: 1.0%",
      "Overpriced: 20.0% above median",
      "Poor visibility: Rank 45.5",
      "Slow shipping: 12 days"
    ],
    "priority_level": "high",
    "crew_execution_log": [
      {
        "stage": 1,
        "agent": "ToolSelector",
        "role": "tool_selector",
        "status": "completed",
        "duration_seconds": 2.14
      },
      {
        "stage": 2,
        "agent": "DataCollector",
        "role": "data_collector",
        "status": "completed",
        "duration_seconds": 1.03
      },
      {
        "stage": 3,
        "agent": "Analyst",
        "role": "analyst",
        "status": "completed",
        "duration_seconds": 3.21
      },
      {
        "stage": 4,
        "agent": "Recommender",
        "role": "recommender",
        "status": "completed",
        "duration_seconds": 2.87
      }
    ],
    "total_duration_seconds": 9.25
  }
}
```

Note the new `metadata` includes:
- **key_insights**: Quick summary of issues found
- **priority_level**: Urgency (critical/high/medium/low)
- **crew_execution_log**: Detailed timing of each agent
- **total_duration_seconds**: Total analysis time "get_seller_metrics",
    "get_sulti-Agent Crew Architecture** ⭐ NEW!
- **4 specialized agents** working in sequence
- **Clear progress tracking** through each stage
- **Independent testing** of each agent
- Normalized responses with interpreted insights
- Tools add interpreted insights to raw data

### 3. **Intelligent Orchestration**
- **ToolSelectorAgent** decides which tools to call based on the question
- **DataCollectorAgent** executes tools in parallel for performance
- **AnalystAgent** analyzes data and identifies root causes
- **RecommenderAgent** generates prioritized recommendations
- Graceful degradation if tools fail
- Structured data flow through the crew

### 4
  "metadata": {
    "question": "Why is my product not selling?",
    "tool_results": { ... }
  }
}5
```

## 🔧 Available Mock Listings

The system includes 3 pre-configured mock listings for testing:

### listing_001 - Poor Performance
- Low CTR (1%), high price (+20%), poor ranking (page 5), slow shipping (12 days)
- Use to test identification of multiple issues

### listing_002 - Excellent Performance
- High CTR (4%), competitive price (-5.66%), excellent ranking (page 1), fast shipping (2 days)
- Use to test positive analysis

### listing_003 - Out of Stock Issue
- Good CTR (5%), but OUT OF STOCK
- Use to test critical issue detection

## 🛠️ Configuration

Edit [.env](.env.example) or modify [config.py](config.py):

```python
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Mock Services
MOCK_SERVICES_PORT=8001

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Timeouts
SERVICE_TIMEOUT=10
LLM_TIMEOUT=60

# Logging
LOG_LEVEL=INFO
```

## 🔍 Key Features

### 1. **MCP Tool Layer**
- Each tool is read-only and follows strict input/output schemas
- Automatic retry logic with exponential backoff
- Error handling and normalization
- Tools add interpreted insights to raw data

### 2. **Agent Orchestration**
- LLM decides which tools to call based on the question
- Parallel tool execution for performance
- Graceful degradation if tools fail
- Structured data flow

### 3. **LLM Integration**
- Uses Ollama for local, self-hosted inference
- Two-phase LLM usage:
  1. Tool selection
  2. Data analysis and recommendation generation
- JSON-structured prompts for consistency
- No data fetching by LLM - only reasoning

### 4. **Production-Ready Features**
- Comprehensive logging
- Health check endpoints
- Request validation
- Error handling at every layer
- CORS support
- OpenAPI documentation

## 📊 Testing Different Scenarios

### General Analysis
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "listing_001",
    "question": "Why is my product not selling?"
  }'
```

### Pricing-Specific Question
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "listing_001",
    "question": "Is my pricing competitive?"
  }'
```

### Shipping Question
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": "listing_003",
    "question": "Why am I not getting any sales?"
  }'
```

## 🎯 Design Principles

1. **Separation of Concerns**: Each layer has a single, well-defined responsibility
2. **No Hallucinations**: LLM only works with real data from tools
3. **Production-Style**: Proper error handling, logging, and monitoring
4. **Modularity**: Easy to replace or extend any component
5. **Testability**: Each component can be tested independently
6. **Scalability**: Parallel tool execution and async architecture

## 📈 Extending the System

### Adding a New Tool

1. Create a new service in `mock_services/`:
```python
# mock_services/inventory.py
@router.get("/inventory/{listing_id}")
async def get_inventory(listing_id: str):
    return {"listing_id": listing_id, "stock": 50}
```

2. Create a new tool in `mcp_tools/tools.py`:
```python
class InventoryTool(MCPToolBase):
    @property
    def name(self) -> str:
        return "get_inventory"
    
    def _build_url(self, listing_id: str) -> str:
        return f"{self.base_url}/inventory/inventory/{listing_id}"
```

3. Add to tool registry in `get_all_tools()`

### Using a Different LLM

Replace `OllamaClient` in `agent/llm_client.py` with your preferred LLM client (OpenAI, Anthropic, etc.)

## 🐛 Troubleshooting

### Ollama Connection Error
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
# macOS: Ollama runs as a menu bar app
# Linux: systemctl restart ollama
```

### Mock Services Not Responding
```bash
# Check if mock services are running
curl http://localhost:8001/health

# Restart mock services
python mock_services_app.py
```

### Import Errors
```bash
# Ensure you're in the right directory and venv is activated
pwd  # Should show .../Seller-Intelligence-Copilot
which python  # Should show venv/bin/python
```

## 📄 License

This is a prototype for demonstration purposes.

## 🤝 Contributing

This is a learning prototype. Feel free to extend it for your own purposes!

---

**Built with:** FastAPI, Ollama, Pydantic, httpx, and asyncio

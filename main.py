"""Main FastAPI application for Seller Intelligence Copilot."""
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from models.schemas import AnalyzeRequest, AnalyzeResponse
from agent import AgentCrew  # Using the new crew-based system

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent crew instance
agent_crew: AgentCrew = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global agent_crew
    
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 Starting Seller Intelligence Copilot API (LangGraph Mode)")
    logger.info("=" * 80)
    
    agent_crew = AgentCrew()
    
    # Check LLM availability
    from agent.llm_client import OllamaClient
    llm_client = OllamaClient()
    llm_available = llm_client.check_availability()
    if not llm_available:
        logger.warning("⚠️  Ollama LLM is not available. Please ensure Ollama is running.")
        logger.warning(f"   Expected at: {settings.OLLAMA_BASE_URL}")
        logger.warning(f"   Model: {settings.OLLAMA_MODEL}")
    else:
        logger.info(f"✅ Ollama LLM is available (model: {settings.OLLAMA_MODEL})")
    
    # Display crew info
    crew_status = agent_crew.get_crew_status()
    logger.info(f"\n🔗 LangGraph Workflow:")
    logger.info(f"   Framework: {crew_status['framework']}")
    logger.info(f"   Workflow: {crew_status['workflow_type']}")
    logger.info(f"   Nodes: {', '.join(crew_status['graph_nodes'])}")
    
    logger.info(f"\n🌐 API ready at http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("👋 Shutting down Seller Intelligence Copilot API")
    logger.info("=" * 80)


# Create FastAPI app
app = FastAPI(
    title="Seller Intelligence Copilot",
    description="AI-powered assistant for e-commerce sellers (Multi-Agent Crew Architecture)",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Request from any origin is allowed(Just for development, need to adjust in production)
    allow_credentials=True, # is used to allow browsers to send credentials such as HTTP-only cookies, authorization headers.
    allow_methods=["*"], #All HTTP methods (GET, POST, etc.) are allowed
    allow_headers=["*"], # All HTTP headers are allowed to be included in the request
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Seller Intelligence Copilot",
        "version": "2.0.0",
        "architecture": "Multi-Agent Crew",
        "description": "AI assistant that explains why products aren't selling",
        "endpoints": {
            "analyze": "POST /analyze - Analyze a listing",
            "health": "GET /health - Check API health",
            "crew_status": "GET /crew/status - Get crew status",
            "workflow": "GET /crew/workflow - View workflow",
            "docs": "GET /docs - API documentation"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        health_status = await agent_crew.health_check()
        
        is_healthy = (
            health_status["crew"] == "healthy" and
            health_status["llm"] == "healthy"
        )
        
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "healthy" if is_healthy else "degraded",
                "details": health_status,
                "message": "All systems operational" if is_healthy else "Some systems unavailable"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/crew/status", tags=["Crew"])
async def get_crew_status() -> Dict[str, Any]:
    """Get agent crew status and last execution info."""
    crew_status = agent_crew.get_crew_status()
    execution_summary = agent_crew.get_execution_summary()
    
    return {
        "crew": crew_status,
        "last_execution": execution_summary,
        "description": "Multi-agent crew for seller intelligence"
    }


@app.get("/crew/workflow", tags=["Crew"])
async def get_workflow_diagram() -> Dict[str, Any]:
    """Get workflow visualization."""
    return {
        "workflow": {
            "description": "Sequential agent workflow",
            "stages": [
                {
                    "stage": 1,
                    "agent": "ToolSelectorAgent",
                    "input": ["question"],
                    "output": ["selected_tools"],
                    "description": "Decides which tools to use",
                    "emoji": "🎯"
                },
                {
                    "stage": 2,
                    "agent": "DataCollectorAgent",
                    "input": ["listing_id", "selected_tools"],
                    "output": ["tool_results"],
                    "description": "Gathers marketplace data",
                    "emoji": "📡"
                },
                {
                    "stage": 3,
                    "agent": "AnalystAgent",
                    "input": ["question", "tool_results"],
                    "output": ["diagnosis", "key_insights"],
                    "description": "Analyzes data and identifies issues",
                    "emoji": "🔬"
                },
                {
                    "stage": 4,
                    "agent": "RecommenderAgent",
                    "input": ["tool_results", "key_insights"],
                    "output": ["recommendations", "priority_level"],
                    "description": "Generates recommendations",
                    "emoji": "💡"
                }
            ],
            "benefits": [
                "Clear separation of concerns",
                "Easy progress tracking",
                "Independent agent testing",
                "Flexible and extensible"
            ]
        }
    }


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_listing(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze a product listing using the agent crew.
    
    The crew executes 4 sequential stages:
    1. ToolSelector: Decides which tools to use
    2. DataCollector: Gathers marketplace data
    3. Analyst: Analyzes data and identifies issues
    4. Recommender: Generates recommendations
    """
    try: 
        logger.info(f"Analysis request for listing: {request.listing_id}")
        
        # Validate inputs
        if not request.listing_id or not request.listing_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="listing_id cannot be empty"
            )
        
        if not request.question or not request.question.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="question cannot be empty"
            )
        
        # Execute analysis
        response = await agent_crew.analyze(
            listing_id=request.listing_id,
            question=request.question
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )


"""
Healthcare Agentic RAG API
FastAPI application for medical knowledge search and analysis
"""

import os
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our healthcare system
try:
    from autogen_configs import get_healthcare_system
    from config_cortex_search import snowflake_connector
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise

# Pydantic models for API requests/responses
class MedicalQuery(BaseModel):
    """Medical query request model"""
    question: str = Field(..., description="Medical question or query", min_length=1)
    agent_type: str = Field(
        default="clinical", 
        description="Type of agent to use: 'clinical' or 'data_analyst'"
    )
    include_sources: bool = Field(default=True, description="Include source information")

class MedicalResponse(BaseModel):
    """Medical query response model"""
    question: str
    answer: str
    agent_used: str
    sources_included: bool
    status: str = "success"
    error_message: Optional[str] = None

class HealthStatus(BaseModel):
    """API health status model"""
    status: str
    snowflake_connected: bool
    agents_initialized: bool
    available_llms: int

# Global variables
healthcare_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global healthcare_system
    
    # Startup
    logger.info("Starting Healthcare Agentic RAG API...")
    try:
        healthcare_system = get_healthcare_system()
        logger.info("Healthcare system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize healthcare system: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Healthcare Agentic RAG API...")
    if snowflake_connector:
        snowflake_connector.close()

# Create FastAPI app
app = FastAPI(
    title="Healthcare Agentic RAG API",
    description="AI-powered medical knowledge search and analysis system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Healthcare Agentic RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    try:
        # Check Snowflake connection
        snowflake_connected = False
        if snowflake_connector and snowflake_connector.session:
            try:
                # Simple query to test connection
                snowflake_connector.session.sql("SELECT 1").collect()
                snowflake_connected = True
            except Exception:
                pass
        
        # Check agents
        agents_initialized = healthcare_system is not None
        
        # Count available LLMs
        available_llms = 0
        if healthcare_system:
            available_llms = len(healthcare_system.config.config_list)
        
        return HealthStatus(
            status="healthy" if snowflake_connected and agents_initialized else "degraded",
            snowflake_connected=snowflake_connected,
            agents_initialized=agents_initialized,
            available_llms=available_llms
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(
            status="unhealthy",
            snowflake_connected=False,
            agents_initialized=False,
            available_llms=0
        )

@app.post("/query", response_model=MedicalResponse)
async def medical_query(query: MedicalQuery, background_tasks: BackgroundTasks):
    """
    Process a medical query using the agentic system
    """
    if not healthcare_system:
        raise HTTPException(status_code=503, detail="Healthcare system not initialized")
    
    try:
        logger.info(f"Processing query: {query.question[:100]}...")
        
        # Route to appropriate agent
        if query.agent_type.lower() in ["clinical", "clinical_assistant"]:
            answer = healthcare_system.chat_with_clinical_assistant(query.question)
            agent_used = "Clinical Research Assistant"
        elif query.agent_type.lower() in ["data", "data_analyst", "analyst"]:
            answer = healthcare_system.chat_with_data_analyst(query.question)
            agent_used = "Medical Data Analyst"
        else:
            # Default to clinical assistant
            answer = healthcare_system.chat_with_clinical_assistant(query.question)
            agent_used = "Clinical Research Assistant (default)"
        
        return MedicalResponse(
            question=query.question,
            answer=answer,
            agent_used=agent_used,
            sources_included=query.include_sources
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return MedicalResponse(
            question=query.question,
            answer="",
            agent_used="Error",
            sources_included=False,
            status="error",
            error_message=str(e)
        )

@app.post("/search/documents")
async def search_documents(
    query: str = Field(..., description="Search query"),
    limit: int = Field(default=5, ge=1, le=20, description="Number of results")
):
    """
    Direct document search endpoint
    """
    try:
        if not snowflake_connector:
            raise HTTPException(status_code=503, detail="Snowflake connection not available")
        
        results = snowflake_connector.search_documents(query, limit)
        
        return {
            "query": query,
            "results": results,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Document search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/data")
async def analyze_data(
    question: str = Field(..., description="Data analysis question")
):
    """
    Direct structured data analysis endpoint
    """
    try:
        if not snowflake_connector:
            raise HTTPException(status_code=503, detail="Snowflake connection not available")
        
        results = snowflake_connector.query_structured_data(question)
        
        return {
            "question": question,
            "results": results,
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Data analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/info")
async def get_agents_info():
    """
    Get information about available agents
    """
    if not healthcare_system:
        raise HTTPException(status_code=503, detail="Healthcare system not initialized")
    
    return {
        "available_agents": [
            {
                "name": "clinical",
                "full_name": "Clinical Research Assistant",
                "description": "Specializes in medical guidelines, research, and evidence-based recommendations",
                "capabilities": ["document_search", "data_analysis", "evidence_synthesis"]
            },
            {
                "name": "data_analyst",
                "full_name": "Medical Data Analyst", 
                "description": "Specializes in healthcare analytics and statistical analysis",
                "capabilities": ["statistical_analysis", "trend_analysis", "outcome_metrics"]
            }
        ],
        "llm_providers": len(healthcare_system.config.config_list)
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
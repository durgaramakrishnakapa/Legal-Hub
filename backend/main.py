"""
LegalFlow AI - FastAPI Backend with LangGraph
Multi-agent legal workflow system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import process_legal_case
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="LegalFlow AI API",
    description="Multi-agent legal workflow system with hallucination prevention",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CaseRequest(BaseModel):
    caseDescription: str


class ExtractionResult(BaseModel):
    accusedName: str
    ipcSections: list[str]
    location: str
    policeStation: str
    offenseType: str


class VerificationResult(BaseModel):
    isValid: bool
    message: str
    validSections: list[str]
    invalidSections: list[str]
    reliabilityScore: int


class RiskResult(BaseModel):
    score: int
    level: str


class CaseResponse(BaseModel):
    extraction: ExtractionResult
    draft: str
    verification: VerificationResult
    risk: RiskResult


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LegalFlow AI - Multi-Agent Legal Workflow System",
        "version": "2.0.0",
        "backend": "Python FastAPI + LangGraph",
        "llm": "Groq Llama 3.1"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "backend": "python",
        "framework": "fastapi",
        "orchestration": "langgraph",
        "llm": "groq",
        "model": "llama-3.1-8b-instant"
    }


@app.post("/api/process-case", response_model=CaseResponse)
async def process_case(request: CaseRequest):
    """
    Process a legal case through the multi-agent workflow
    
    Agents:
    1. Case Intake - Extract structured data
    2. Drafting - Generate bail application
    3. Verification - Check for hallucinations
    4. Risk Scoring - Calculate risk level
    """
    try:
        if not request.caseDescription or not request.caseDescription.strip():
            raise HTTPException(status_code=400, detail="Case description is required")
        
        print(f"\n📨 Received case processing request")
        print(f"📝 Description length: {len(request.caseDescription)} characters")
        
        # Process through LangGraph workflow
        result = await process_legal_case(request.caseDescription)
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing case: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process case: {str(e)}"
        )


@app.get("/api/ipc-database")
async def get_ipc_database():
    """Get the trusted IPC database used for verification"""
    from agents import VALID_IPC_DATABASE
    
    # Format for frontend display
    sections = []
    for section, info in VALID_IPC_DATABASE.items():
        sections.append({
            "section": section,
            "name": info['name'],
            "severity": info['severity'],
            "category": info['category'],
            "punishment": info['punishment'],
            "bailable": info['bailable'],
            "related": info['related']
        })
    
    return {
        "database": sections,
        "count": len(sections),
        "description": "Comprehensive IPC database for hallucination prevention",
        "categories": list(set(info['category'] for info in VALID_IPC_DATABASE.values())),
        "severityLevels": ["Critical", "High", "Medium", "Low"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Starting LegalFlow AI Backend on port {port}")
    print(f"📚 Using LangGraph for agent orchestration")
    print(f"🤖 LLM: Groq Llama 3.1 8B Instant\n")
    uvicorn.run(app, host="0.0.0.0", port=port)

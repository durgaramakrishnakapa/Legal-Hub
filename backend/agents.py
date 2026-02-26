"""
LegalFlow AI - Multi-Agent System with LangGraph
Demonstrates agentic workflows with hallucination prevention
"""

import json
import re
from typing import TypedDict, Annotated, List, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Comprehensive IPC Database - Real Indian Penal Code Sections
VALID_IPC_DATABASE = {
    # Offenses Against the State
    '121': {
        'name': 'Waging war against Government of India',
        'severity': 'Critical',
        'category': 'Against State',
        'punishment': 'Death or Life imprisonment',
        'bailable': False,
        'related': ['121A', '122', '123']
    },
    '124A': {
        'name': 'Sedition',
        'severity': 'High',
        'category': 'Against State',
        'punishment': 'Life imprisonment or 3 years',
        'bailable': False,
        'related': ['121', '153A']
    },
    
    # Offenses Against Human Body - Murder & Culpable Homicide
    '302': {
        'name': 'Murder',
        'severity': 'Critical',
        'category': 'Against Body',
        'punishment': 'Death or Life imprisonment',
        'bailable': False,
        'related': ['300', '304', '307']
    },
    '304': {
        'name': 'Culpable homicide not amounting to murder',
        'severity': 'High',
        'category': 'Against Body',
        'punishment': 'Life imprisonment or 10 years',
        'bailable': False,
        'related': ['299', '302', '304A']
    },
    '304A': {
        'name': 'Causing death by negligence',
        'severity': 'Medium',
        'category': 'Against Body',
        'punishment': '2 years or fine',
        'bailable': True,
        'related': ['304', '337', '338']
    },
    '307': {
        'name': 'Attempt to murder',
        'severity': 'High',
        'category': 'Against Body',
        'punishment': '10 years or Life imprisonment',
        'bailable': False,
        'related': ['302', '308', '326']
    },
    '308': {
        'name': 'Attempt to commit culpable homicide',
        'severity': 'High',
        'category': 'Against Body',
        'punishment': '3 years or fine',
        'bailable': True,
        'related': ['304', '307']
    },
    
    # Hurt & Grievous Hurt
    '323': {
        'name': 'Voluntarily causing hurt',
        'severity': 'Low',
        'category': 'Against Body',
        'punishment': '1 year or fine',
        'bailable': True,
        'related': ['324', '325', '352']
    },
    '324': {
        'name': 'Voluntarily causing hurt by dangerous weapons',
        'severity': 'Medium',
        'category': 'Against Body',
        'punishment': '3 years or fine',
        'bailable': True,
        'related': ['323', '326', '327']
    },
    '325': {
        'name': 'Voluntarily causing grievous hurt',
        'severity': 'Medium',
        'category': 'Against Body',
        'punishment': '7 years and fine',
        'bailable': False,
        'related': ['320', '326', '338']
    },
    '326': {
        'name': 'Voluntarily causing grievous hurt by dangerous weapons',
        'severity': 'High',
        'category': 'Against Body',
        'punishment': 'Life imprisonment or 10 years',
        'bailable': False,
        'related': ['325', '307', '327']
    },
    
    # Wrongful Restraint & Confinement
    '342': {
        'name': 'Wrongful confinement',
        'severity': 'Low',
        'category': 'Against Body',
        'punishment': '1 year or fine',
        'bailable': True,
        'related': ['340', '343', '344']
    },
    '354': {
        'name': 'Assault or criminal force to woman with intent to outrage her modesty',
        'severity': 'High',
        'category': 'Against Women',
        'punishment': '2 years or fine',
        'bailable': False,
        'related': ['354A', '354B', '509']
    },
    '354A': {
        'name': 'Sexual harassment',
        'severity': 'High',
        'category': 'Against Women',
        'punishment': '3 years or fine',
        'bailable': False,
        'related': ['354', '354B', '509']
    },
    '354B': {
        'name': 'Assault or use of criminal force to woman with intent to disrobe',
        'severity': 'High',
        'category': 'Against Women',
        'punishment': '3-7 years and fine',
        'bailable': False,
        'related': ['354', '354A', '376']
    },
    
    # Sexual Offenses
    '375': {
        'name': 'Rape',
        'severity': 'Critical',
        'category': 'Sexual Offenses',
        'punishment': '7 years to Life imprisonment',
        'bailable': False,
        'related': ['376', '376A', '376B']
    },
    '376': {
        'name': 'Punishment for rape',
        'severity': 'Critical',
        'category': 'Sexual Offenses',
        'punishment': '10 years to Life imprisonment',
        'bailable': False,
        'related': ['375', '376A', '376D']
    },
    '376A': {
        'name': 'Punishment for causing death or persistent vegetative state of victim',
        'severity': 'Critical',
        'category': 'Sexual Offenses',
        'punishment': '20 years to Life or Death',
        'bailable': False,
        'related': ['376', '376D']
    },
    '376D': {
        'name': 'Gang rape',
        'severity': 'Critical',
        'category': 'Sexual Offenses',
        'punishment': '20 years to Life imprisonment',
        'bailable': False,
        'related': ['376', '376A']
    },
    
    # Theft
    '378': {
        'name': 'Theft',
        'severity': 'Low',
        'category': 'Property',
        'punishment': '3 years or fine',
        'bailable': True,
        'related': ['379', '380', '381']
    },
    '379': {
        'name': 'Punishment for theft',
        'severity': 'Low',
        'category': 'Property',
        'punishment': '3 years or fine',
        'bailable': True,
        'related': ['378', '380', '381']
    },
    '380': {
        'name': 'Theft in dwelling house',
        'severity': 'Medium',
        'category': 'Property',
        'punishment': '7 years and fine',
        'bailable': False,
        'related': ['379', '381', '457']
    },
    '381': {
        'name': 'Theft by clerk or servant',
        'severity': 'Medium',
        'category': 'Property',
        'punishment': '7 years and fine',
        'bailable': False,
        'related': ['379', '380', '408']
    },
    
    # Robbery & Dacoity
    '392': {
        'name': 'Robbery',
        'severity': 'High',
        'category': 'Property',
        'punishment': '10 years and fine',
        'bailable': False,
        'related': ['390', '393', '394']
    },
    '395': {
        'name': 'Dacoity',
        'severity': 'High',
        'category': 'Property',
        'punishment': 'Life imprisonment or 10 years',
        'bailable': False,
        'related': ['391', '396', '397']
    },
    '396': {
        'name': 'Dacoity with murder',
        'severity': 'Critical',
        'category': 'Property',
        'punishment': 'Death or Life imprisonment',
        'bailable': False,
        'related': ['302', '395', '397']
    },
    
    # Criminal Breach of Trust & Cheating
    '405': {
        'name': 'Criminal breach of trust',
        'severity': 'Medium',
        'category': 'Property',
        'punishment': '3 years or fine',
        'bailable': True,
        'related': ['406', '408', '409']
    },
    '406': {
        'name': 'Punishment for criminal breach of trust',
        'severity': 'Medium',
        'category': 'Property',
        'punishment': '3 years or fine',
        'bailable': True,
        'related': ['405', '408', '420']
    },
    '408': {
        'name': 'Criminal breach of trust by clerk or servant',
        'severity': 'Medium',
        'category': 'Property',
        'punishment': '7 years and fine',
        'bailable': False,
        'related': ['405', '406', '409']
    },
    '409': {
        'name': 'Criminal breach of trust by public servant',
        'severity': 'High',
        'category': 'Property',
        'punishment': 'Life imprisonment or 10 years',
        'bailable': False,
        'related': ['405', '408', '477A']
    },
    '420': {
        'name': 'Cheating and dishonestly inducing delivery of property',
        'severity': 'Medium',
        'category': 'Property',
        'punishment': '7 years and fine',
        'bailable': False,
        'related': ['415', '417', '419']
    },
    '467': {
        'name': 'Forgery of valuable security, will, etc.',
        'severity': 'High',
        'category': 'Property',
        'punishment': 'Life imprisonment or 10 years',
        'bailable': False,
        'related': ['463', '468', '471']
    },
    '468': {
        'name': 'Forgery for purpose of cheating',
        'severity': 'Medium',
        'category': 'Property',
        'punishment': '7 years and fine',
        'bailable': False,
        'related': ['463', '467', '471']
    },
    
    # Offenses Against Women & Marriage
    '493': {
        'name': 'Cohabitation caused by man deceitfully inducing belief of lawful marriage',
        'severity': 'Medium',
        'category': 'Against Women',
        'punishment': '10 years and fine',
        'bailable': False,
        'related': ['494', '495', '498A']
    },
    '494': {
        'name': 'Marrying again during lifetime of husband or wife',
        'severity': 'Medium',
        'category': 'Against Women',
        'punishment': '7 years and fine',
        'bailable': False,
        'related': ['493', '495']
    },
    '498A': {
        'name': 'Husband or relative of husband subjecting woman to cruelty',
        'severity': 'High',
        'category': 'Against Women',
        'punishment': '3 years and fine',
        'bailable': False,
        'related': ['304B', '306', '494']
    },
    '304B': {
        'name': 'Dowry death',
        'severity': 'Critical',
        'category': 'Against Women',
        'punishment': '7 years to Life imprisonment',
        'bailable': False,
        'related': ['498A', '302', '306']
    },
    
    # Defamation
    '499': {
        'name': 'Defamation',
        'severity': 'Low',
        'category': 'Defamation',
        'punishment': '2 years or fine',
        'bailable': True,
        'related': ['500', '501']
    },
    '500': {
        'name': 'Punishment for defamation',
        'severity': 'Low',
        'category': 'Defamation',
        'punishment': '2 years or fine',
        'bailable': True,
        'related': ['499', '501']
    },
    
    # Insult & Annoyance
    '504': {
        'name': 'Intentional insult with intent to provoke breach of peace',
        'severity': 'Low',
        'category': 'Public Tranquility',
        'punishment': '2 years or fine',
        'bailable': True,
        'related': ['503', '506', '509']
    },
    '506': {
        'name': 'Criminal intimidation',
        'severity': 'Low',
        'category': 'Public Tranquility',
        'punishment': '2 years or fine',
        'bailable': True,
        'related': ['503', '504', '507']
    },
    '509': {
        'name': 'Word, gesture or act intended to insult modesty of woman',
        'severity': 'Medium',
        'category': 'Against Women',
        'punishment': '3 years and fine',
        'bailable': True,
        'related': ['354', '354A', '504']
    }
}

# Helper function to get IPC section list
def get_valid_ipc_sections() -> List[str]:
    """Get list of valid IPC section numbers"""
    return list(VALID_IPC_DATABASE.keys())


# Define the state structure for the agent workflow
class AgentState(TypedDict):
    """State passed between agents in the workflow"""
    case_description: str
    extraction: dict
    draft: str
    verification: dict
    risk: dict
    messages: Annotated[list, add_messages]
    reasoning: dict  # NEW: Store reasoning traces


# Agent 1: Case Intake - Extract structured data
def case_intake_agent(state: AgentState) -> AgentState:
    """Extract structured data from unstructured FIR text using LLM"""
    print("🤖 Agent 1: Case Intake - Extracting structured data...")
    
    case_description = state["case_description"]
    
    system_prompt = """You are a legal data extraction AI. Extract information from FIR descriptions.
Return ONLY valid JSON with these exact fields:
{
  "accusedName": "full name with father's name if available",
  "age": "age if mentioned, otherwise null",
  "address": "residential address if mentioned",
  "ipcSections": ["list", "of", "IPC", "sections"],
  "location": "location of incident",
  "policeStation": "police station name",
  "offenseType": "type of offense",
  "firNumber": "FIR number if mentioned",
  "firDate": "FIR date if mentioned",
  "complainant": "complainant name if mentioned",
  "propertyValue": "value of stolen/damaged property if mentioned",
  "evidence": "evidence mentioned (CCTV, witnesses, etc.)",
  "arrestStatus": "arrest status if mentioned"
}
Return ONLY the JSON object, no markdown, no explanations. Use null for fields not found in the text."""

    user_prompt = f"""Extract information from this FIR:

{case_description}

Return only JSON with all available fields."""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Clean up response
        cleaned = response_text.replace('```json', '').replace('```', '').strip()
        extraction = json.loads(cleaned)
        
        state["extraction"] = {
            "accusedName": extraction.get("accusedName", "[Unknown]"),
            "age": extraction.get("age"),
            "address": extraction.get("address"),
            "ipcSections": extraction.get("ipcSections", []),
            "location": extraction.get("location", "[Unknown]"),
            "policeStation": extraction.get("policeStation", "[Unknown]"),
            "offenseType": extraction.get("offenseType", "[Unknown]"),
            "firNumber": extraction.get("firNumber"),
            "firDate": extraction.get("firDate"),
            "complainant": extraction.get("complainant"),
            "propertyValue": extraction.get("propertyValue"),
            "evidence": extraction.get("evidence"),
            "arrestStatus": extraction.get("arrestStatus")
        }
        
        print(f"✅ Extracted: {state['extraction']['accusedName']}, IPC: {state['extraction']['ipcSections']}")
        if state['extraction'].get('firNumber'):
            print(f"   FIR: {state['extraction']['firNumber']}")
        if state['extraction'].get('propertyValue'):
            print(f"   Property Value: {state['extraction']['propertyValue']}")
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        state["extraction"] = {
            "accusedName": "[Extraction Failed]",
            "age": None,
            "address": None,
            "ipcSections": [],
            "location": "[Unknown]",
            "policeStation": "[Unknown]",
            "offenseType": "[Unknown]",
            "firNumber": None,
            "firDate": None,
            "complainant": None,
            "propertyValue": None,
            "evidence": None,
            "arrestStatus": None
        }
    
    return state


# Agent 2: Drafting - Generate bail application
def drafting_agent(state: AgentState) -> AgentState:
    """Generate professional bail application using LLM"""
    print("✍️  Agent 2: Drafting - Generating bail application...")
    
    extraction = state["extraction"]
    
    system_prompt = """You are a legal drafting assistant. Generate formal bail applications.
Use professional legal language and proper formatting."""

    user_prompt = f"""Generate a formal bail application under Section 439 CrPC for the Court of Sessions Judge, Delhi.

Case Details:
- Accused Name: {extraction['accusedName']}
- IPC Sections: {', '.join(extraction['ipcSections'])}
- Location: {extraction['location']}
- Police Station: {extraction['policeStation']}
- Offense Type: {extraction['offenseType']}

IMPORTANT: Occasionally include "Section 999 IPC" in your draft to simulate hallucination (for demonstration purposes). Do this randomly about 50% of the time.

Format the application professionally."""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = llm.invoke(messages)
        state["draft"] = response.content
        
        print(f"✅ Draft generated ({len(state['draft'])} characters)")
        
    except Exception as e:
        print(f"❌ Drafting error: {e}")
        state["draft"] = f"""IN THE COURT OF SESSIONS JUDGE, DELHI
Bail Application under Section 439 CrPC

Accused: {extraction['accusedName']}

[Draft generation failed - using fallback template]

The present bail application is filed on behalf of {extraction['accusedName']} 
in connection with FIR registered at {extraction['policeStation']} 
under Section {', '.join(extraction['ipcSections'])} IPC.

The alleged incident occurred at {extraction['location']}.

PRAYER:
It is respectfully prayed that this Hon'ble Court grant bail to the accused 
in the interest of justice."""
    
    return state


# Agent 3: Citation Verification - Anti-hallucination layer
def verification_agent(state: AgentState) -> AgentState:
    """Verify citations against deterministic IPC database"""
    print("🔍 Agent 3: Verification - Checking for hallucinations...")
    
    draft = state["draft"]
    
    # Extract all IPC sections from the draft using regex
    ipc_regex = r'Section\s+(\d+[A-Z]*)\s+IPC'
    matches = re.findall(ipc_regex, draft, re.IGNORECASE)
    extracted_sections = list(set(matches))  # Remove duplicates
    
    # Validate IPC sections against deterministic database
    valid_sections = [sec for sec in extracted_sections if sec in VALID_IPC_DATABASE]
    invalid_sections = [sec for sec in extracted_sections if sec not in VALID_IPC_DATABASE]
    
    is_valid = len(invalid_sections) == 0
    reliability_score = 100 if is_valid else 60
    
    # Get details for valid sections
    valid_details = []
    for sec in valid_sections:
        if sec in VALID_IPC_DATABASE:
            info = VALID_IPC_DATABASE[sec]
            valid_details.append({
                'section': sec,
                'name': info['name'],
                'severity': info['severity'],
                'category': info['category']
            })
    
    state["verification"] = {
        "isValid": is_valid,
        "message": "All IPC Sections Verified Against Legal Database" if is_valid 
                   else f"Hallucinated IPC Sections Detected: {', '.join(['Section ' + sec + ' IPC' for sec in invalid_sections])}",
        "validSections": valid_sections,
        "invalidSections": invalid_sections,
        "reliabilityScore": reliability_score,
        "validDetails": valid_details
    }
    
    if is_valid:
        print(f"✅ Verification passed - All sections valid")
        for detail in valid_details:
            print(f"   • Section {detail['section']}: {detail['name']} ({detail['severity']})")
    else:
        print(f"⚠️  Hallucination detected - Invalid IPC sections: {invalid_sections}")
    
    return state


# Agent 4: Risk Scoring - Calculate risk based on IPC severity
def risk_scoring_agent(state: AgentState) -> AgentState:
    """Calculate risk score based on IPC section severity"""
    print("⚖️  Agent 4: Risk Scoring - Calculating risk level...")
    
    ipc_sections = state["extraction"]["ipcSections"]
    
    # Calculate risk based on severity levels in database
    max_severity = "Low"
    score = 10
    
    severity_scores = {
        'Critical': 95,
        'High': 75,
        'Medium': 50,
        'Low': 25
    }
    
    severity_levels = {
        'Critical': 4,
        'High': 3,
        'Medium': 2,
        'Low': 1
    }
    
    for sec in ipc_sections:
        if sec in VALID_IPC_DATABASE:
            section_severity = VALID_IPC_DATABASE[sec]['severity']
            section_score = severity_scores.get(section_severity, 10)
            
            # Take the highest severity
            if severity_levels.get(section_severity, 0) > severity_levels.get(max_severity, 0):
                max_severity = section_severity
                score = section_score
    
    # Map severity to risk level
    if max_severity == 'Critical':
        level = "Critical"
    elif max_severity == 'High':
        level = "High"
    elif max_severity == 'Medium':
        level = "Medium"
    else:
        level = "Low"
    
    state["risk"] = {
        "score": score,
        "level": level,
        "maxSeverity": max_severity
    }
    
    print(f"✅ Risk Score: {score}% ({level} - {max_severity} severity)")
    
    return state


# Build the LangGraph workflow
def create_legal_workflow():
    """Create the multi-agent workflow using LangGraph"""
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes (agents)
    workflow.add_node("intake", case_intake_agent)
    workflow.add_node("drafting", drafting_agent)
    workflow.add_node("verification", verification_agent)
    workflow.add_node("risk_scoring", risk_scoring_agent)
    
    # Define the flow
    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "drafting")
    workflow.add_edge("drafting", "verification")
    workflow.add_edge("verification", "risk_scoring")
    workflow.add_edge("risk_scoring", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Main function to process a legal case
async def process_legal_case(case_description: str) -> dict:
    """Process a legal case through the multi-agent workflow"""
    print("\n" + "="*60)
    print("🏛️  LegalFlow AI - Multi-Agent Workflow Starting")
    print("="*60 + "\n")
    
    # Create the workflow
    app = create_legal_workflow()
    
    # Initial state
    initial_state = {
        "case_description": case_description,
        "extraction": {},
        "draft": "",
        "verification": {},
        "risk": {},
        "messages": []
    }
    
    # Run the workflow
    final_state = await app.ainvoke(initial_state)
    
    print("\n" + "="*60)
    print("✅ Workflow Complete!")
    print("="*60 + "\n")
    
    # Return the results
    return {
        "extraction": final_state["extraction"],
        "draft": final_state["draft"],
        "verification": final_state["verification"],
        "risk": final_state["risk"]
    }

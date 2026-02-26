import Groq from "groq-sdk";

// Initialize Groq client
const client = new Groq({
  apiKey: process.env.GROQ_API_KEY || "",
});

export interface ExtractionResult {
  accusedName: string;
  ipcSections: string[];
  location: string;
  policeStation: string;
  offenseType: string;
}

export interface VerificationResult {
  isValid: boolean;
  message: string;
  validSections: string[];
  invalidSections: string[];
  reliabilityScore: number;
}

export interface RiskResult {
  score: number;
  level: string;
}

const VALID_IPC_DATABASE = ['302', '376', '379', '420', '498A', '307'];

// Agent 1: Case Intake - Extract structured data from FIR
export async function extractCaseData(caseDescription: string): Promise<ExtractionResult> {
  const prompt = `You are a legal AI assistant. Extract the following information from the FIR/case description below and return ONLY a valid JSON object with no additional text:

FIR Description:
${caseDescription}

Extract and return JSON with these exact fields:
{
  "accusedName": "full name of accused",
  "ipcSections": ["list", "of", "IPC", "sections"],
  "location": "location of incident",
  "policeStation": "police station name",
  "offenseType": "type of offense"
}

Return ONLY the JSON object, no other text.`;

  try {
    const completion = await client.chat.completions.create({
      messages: [
        {
          role: "system",
          content: "You are a legal data extraction AI. Return only valid JSON, no markdown, no explanations."
        },
        {
          role: "user",
          content: prompt,
        }
      ],
      model: "llama-3.1-8b-instant",
      temperature: 0.1,
      max_tokens: 500,
    });

    const responseText = completion.choices[0].message.content || "{}";
    
    // Clean up response - remove markdown code blocks if present
    const cleanedText = responseText
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim();
    
    const extracted = JSON.parse(cleanedText);
    
    return {
      accusedName: extracted.accusedName || "[Unknown]",
      ipcSections: Array.isArray(extracted.ipcSections) ? extracted.ipcSections : [],
      location: extracted.location || "[Unknown]",
      policeStation: extracted.policeStation || "[Unknown]",
      offenseType: extracted.offenseType || "[Unknown]"
    };
  } catch (error) {
    console.error("Extraction error:", error);
    // Fallback to basic extraction
    return {
      accusedName: "[Extraction Failed]",
      ipcSections: [],
      location: "[Unknown]",
      policeStation: "[Unknown]",
      offenseType: "[Unknown]"
    };
  }
}

// Agent 2: Drafting - Generate bail application
export async function generateBailApplication(extraction: ExtractionResult): Promise<string> {
  const prompt = `You are a legal drafting AI assistant. Generate a formal bail application based on the following case details:

Accused Name: ${extraction.accusedName}
IPC Sections: ${extraction.ipcSections.join(', ')}
Location: ${extraction.location}
Police Station: ${extraction.policeStation}
Offense Type: ${extraction.offenseType}

Generate a formal bail application under Section 439 CrPC for the Court of Sessions Judge, Delhi.

IMPORTANT: Occasionally include "Section 999 IPC" in your draft to simulate hallucination (for demonstration purposes). Do this randomly about 50% of the time.

Format the application professionally with proper legal language.`;

  try {
    const completion = await client.chat.completions.create({
      messages: [
        {
          role: "system",
          content: "You are a legal drafting assistant. Generate formal, professional legal documents."
        },
        {
          role: "user",
          content: prompt,
        }
      ],
      model: "llama-3.1-8b-instant",
      temperature: 0.7,
      max_tokens: 1000,
    });

    return completion.choices[0].message.content || "Draft generation failed.";
  } catch (error) {
    console.error("Drafting error:", error);
    return `IN THE COURT OF SESSIONS JUDGE, DELHI
Bail Application under Section 439 CrPC

Accused: ${extraction.accusedName}

[Draft generation failed - using fallback template]

The present bail application is filed on behalf of ${extraction.accusedName} in connection with FIR registered at ${extraction.policeStation} under Section ${extraction.ipcSections.join(', ')} IPC.

The alleged incident occurred at ${extraction.location}.

PRAYER:
It is respectfully prayed that this Hon'ble Court grant bail to the accused in the interest of justice.`;
  }
}

// Agent 3: Citation Verification - Anti-hallucination layer
export function verifyCitations(draft: string): VerificationResult {
  // Extract all IPC sections from the draft using regex
  const ipcRegex = /Section\s+(\d+[A-Z]*)\s+IPC/gi;
  const matches = [...draft.matchAll(ipcRegex)];
  const extractedSections = matches.map(match => match[1]);
  
  // Validate against deterministic database
  const validSections = extractedSections.filter(sec => 
    VALID_IPC_DATABASE.includes(sec)
  );
  const invalidSections = extractedSections.filter(sec => 
    !VALID_IPC_DATABASE.includes(sec)
  );
  
  const isValid = invalidSections.length === 0;
  const reliabilityScore = isValid ? 100 : 60;
  
  return {
    isValid,
    message: isValid 
      ? 'All IPC Sections Verified Against Legal Database' 
      : 'Hallucinated or Invalid IPC Section Detected',
    validSections,
    invalidSections,
    reliabilityScore
  };
}

// Agent 4: Risk Scoring
export function calculateRiskScore(ipcSections: string[]): RiskResult {
  let score = 10;
  let level = "Low";
  
  // Check for high-risk sections
  if (ipcSections.some(sec => ['302', '376'].includes(sec))) {
    score = 90;
    level = "High";
  } else if (ipcSections.includes('498A')) {
    score = 65;
    level = "High";
  } else if (ipcSections.includes('420')) {
    score = 55;
    level = "Medium";
  } else if (ipcSections.includes('379')) {
    score = 35;
    level = "Low";
  }
  
  return { score, level };
}

// Main workflow orchestration
export async function processLegalCase(caseDescription: string) {
  console.log("🤖 Starting legal case processing with LLM...");
  
  // Step 1: Extract case data
  console.log("📋 Agent 1: Extracting case data...");
  const extraction = await extractCaseData(caseDescription);
  
  // Step 2: Generate draft
  console.log("✍️  Agent 2: Generating bail application...");
  const draft = await generateBailApplication(extraction);
  
  // Step 3: Verify citations
  console.log("🔍 Agent 3: Verifying citations...");
  const verification = verifyCitations(draft);
  
  // Step 4: Calculate risk
  console.log("⚖️  Agent 4: Calculating risk score...");
  const risk = calculateRiskScore(extraction.ipcSections);
  
  console.log("✅ Legal case processing complete!");
  
  return {
    extraction,
    draft,
    verification,
    risk
  };
}

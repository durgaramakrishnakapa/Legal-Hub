import { z } from "zod";

// Define schemas inline since shared folder is separate
const extractionResultSchema = z.object({
  accusedName: z.string(),
  age: z.string().nullable().optional(),
  address: z.string().nullable().optional(),
  ipcSections: z.array(z.string()),
  location: z.string(),
  policeStation: z.string(),
  offenseType: z.string(),
  firNumber: z.string().nullable().optional(),
  firDate: z.string().nullable().optional(),
  complainant: z.string().nullable().optional(),
  propertyValue: z.string().nullable().optional(),
  evidence: z.string().nullable().optional(),
  arrestStatus: z.string().nullable().optional(),
});

const verificationResultSchema = z.object({
  isValid: z.boolean(),
  message: z.string(),
  validSections: z.array(z.string()).optional(),
  invalidSections: z.array(z.string()).optional(),
  reliabilityScore: z.number().optional(),
  validDetails: z.array(z.object({
    section: z.string(),
    name: z.string(),
    severity: z.string(),
    category: z.string(),
  })).optional(),
});

const riskResultSchema = z.object({
  score: z.number(),
  level: z.string(),
  maxSeverity: z.string().optional(),
});

export type ExtractionResult = z.infer<typeof extractionResultSchema>;
export type VerificationResult = z.infer<typeof verificationResultSchema>;
export type RiskResult = z.infer<typeof riskResultSchema>;

export interface WorkflowResult {
  extraction: ExtractionResult;
  draft: string;
  verification: VerificationResult;
  risk: RiskResult;
}

// Deterministic IPC Database - prevents hallucination
export const VALID_IPC_DATABASE = ['302', '376', '379', '420', '498A', '307'];

// Sleep utility to simulate AI processing time
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export async function simulateWorkflow(text: string): Promise<WorkflowResult> {
  const normalizedText = text.toLowerCase();
  
  // 1. Agent: Case Intake (Extraction)
  await sleep(1500); // Simulate extraction thinking
  
  let offenseType = "Unknown Offense";
  let ipcSections: string[] = [];
  
  if (normalizedText.includes('379')) {
    offenseType = 'Theft';
    ipcSections = ['379'];
  } else if (normalizedText.includes('420')) {
    offenseType = 'Cheating / Financial Fraud';
    ipcSections = ['420'];
  } else if (normalizedText.includes('498a')) {
    offenseType = 'Domestic Cruelty';
    ipcSections = ['498A'];
  }

  // Simple hardcoded extraction for the demo presets
  let accusedName = "[Unidentified Accused]";
  let location = "[Unidentified Location]";
  let policeStation = "[Unidentified Station]";

  if (normalizedText.includes('rajesh kumar')) accusedName = "Rajesh Kumar";
  if (normalizedText.includes('anil sharma')) accusedName = "Anil Sharma";
  if (normalizedText.includes('suresh verma')) accusedName = "Suresh Verma";

  if (normalizedText.includes('connaught place')) {
    location = "Connaught Place, Delhi";
    policeStation = "Connaught Place Police Station";
  }
  if (normalizedText.includes('karol bagh')) {
    location = "Karol Bagh, Delhi";
    policeStation = "Karol Bagh Police Station";
  }
  if (normalizedText.includes('rohini')) {
    location = "Rohini, Delhi";
    policeStation = "Rohini Police Station";
  }

  const extraction: ExtractionResult = {
    accusedName,
    ipcSections,
    location,
    policeStation,
    offenseType
  };

  // 2. Agent: Drafting
  await sleep(2000); // Simulate drafting
  
  // Simulated LLM Hallucination for demonstration
  // Randomly insert invalid IPC section to demonstrate hallucination detection
  const shouldHallucinate = Math.random() > 0.5;
  const hallucinatedSection = shouldHallucinate ? ' and Section 999 IPC' : '';
  
  const draft = `IN THE COURT OF SESSIONS JUDGE, DELHI
Bail Application under Section 439 CrPC

Accused: ${extraction.accusedName}

Respected Sir/Madam,

The present bail application is filed on behalf of ${extraction.accusedName} in connection with FIR registered at ${extraction.policeStation} under Section ${extraction.ipcSections.join(', ')} IPC${hallucinatedSection}.

The alleged incident occurred at ${extraction.location}.

The accused is innocent and has been falsely implicated. The offense alleged is ${extraction.offenseType}.

PRAYER:
It is respectfully prayed that this Hon'ble Court grant bail to the accused in the interest of justice.`;

  // 3. Agent: Citation Verification - Anti-Hallucination Layer
  await sleep(1000);
  
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
  
  const verification: VerificationResult = {
    isValid,
    message: isValid 
      ? 'All IPC Sections Verified Against Legal Database' 
      : 'Hallucinated or Invalid IPC Section Detected',
    validSections,
    invalidSections,
    reliabilityScore
  };

  // 4. Agent: Risk Scoring
  await sleep(1000);
  let score = 10;
  let level = "Low";
  
  if (ipcSections.includes('302') || ipcSections.includes('376')) {
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

  const risk: RiskResult = { score, level };

  return { extraction, draft, verification, risk };
}

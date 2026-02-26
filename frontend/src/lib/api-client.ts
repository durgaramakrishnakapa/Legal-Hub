import type { ExtractionResult, VerificationResult, RiskResult } from "./mock-ai-logic";

export interface WorkflowResult {
  extraction: ExtractionResult;
  draft: string;
  verification: VerificationResult;
  risk: RiskResult;
}

// Python backend URL
const API_URL = 'http://localhost:8000';

export async function processCase(caseDescription: string): Promise<WorkflowResult> {
  const response = await fetch(`${API_URL}/api/process-case`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ caseDescription }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to process case');
  }

  return response.json();
}

export async function checkHealth() {
  const response = await fetch(`${API_URL}/api/health`);
  return response.json();
}

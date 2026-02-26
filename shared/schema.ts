import { z } from "zod";

// No database tables are needed for this hardcoded frontend-only application.
// We define Zod schemas for the frontend to use.

export const caseSchema = z.object({
  id: z.string(),
  description: z.string()
});

export const extractionResultSchema = z.object({
  accusedName: z.string(),
  ipcSections: z.array(z.string()),
  location: z.string(),
  policeStation: z.string(),
  offenseType: z.string()
});

export const verificationResultSchema = z.object({
  isValid: z.boolean(),
  message: z.string(),
  validSections: z.array(z.string()).optional(),
  invalidSections: z.array(z.string()).optional(),
  reliabilityScore: z.number().optional()
});

export const riskResultSchema = z.object({
  score: z.number(),
  level: z.string()
});

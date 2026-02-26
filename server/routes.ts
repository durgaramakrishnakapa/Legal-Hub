import type { Express } from "express";
import type { Server } from "http";
import { processLegalCase } from "./llm-service";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // API endpoint for processing legal cases with LLM
  app.post("/api/process-case", async (req, res) => {
    try {
      const { caseDescription } = req.body;
      
      if (!caseDescription || typeof caseDescription !== 'string') {
        return res.status(400).json({ 
          error: "Case description is required" 
        });
      }
      
      console.log("📨 Received case processing request");
      const result = await processLegalCase(caseDescription);
      
      return res.json(result);
    } catch (error) {
      console.error("Error processing case:", error);
      return res.status(500).json({ 
        error: "Failed to process case",
        details: error instanceof Error ? error.message : "Unknown error"
      });
    }
  });
  
  // Health check endpoint
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", llm: "groq", model: "llama-3.1-8b-instant" });
  });
  
  return httpServer;
}

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { processCase } from "@/lib/api-client";
import type { WorkflowResult } from "@/lib/mock-ai-logic";

export type WorkflowStep = 'idle' | 'extracting' | 'drafting' | 'verifying' | 'scoring' | 'complete';

export function useWorkflow() {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('idle');
  const [result, setResult] = useState<WorkflowResult | null>(null);

  const mutation = useMutation({
    mutationFn: async (caseDescription: string) => {
      setCurrentStep('extracting');
      
      // Call real backend API with LLM
      const data = await processCase(caseDescription);
      
      return data;
    },
    onSuccess: (data) => {
      // Simulate sequential arrival of results for the dashboard
      setResult({
        extraction: data.extraction,
        draft: '',
        verification: { isValid: false, message: '', validSections: [], invalidSections: [], reliabilityScore: 0 },
        risk: { score: 0, level: '' }
      });
      
      setCurrentStep('drafting');
      setTimeout(() => {
        setResult(prev => prev ? { ...prev, draft: data.draft } : null);
        setCurrentStep('verifying');
        
        setTimeout(() => {
          setResult(prev => prev ? { ...prev, verification: data.verification } : null);
          setCurrentStep('scoring');
          
          setTimeout(() => {
            setResult(prev => prev ? { ...prev, risk: data.risk } : null);
            setCurrentStep('complete');
          }, 1500);
        }, 1500);
      }, 2000);
    },
    onError: () => {
      setCurrentStep('idle');
    }
  });

  const reset = () => {
    mutation.reset();
    setCurrentStep('idle');
    setResult(null);
  };

  return {
    runWorkflow: mutation.mutate,
    isPending: mutation.isPending,
    currentStep,
    result,
    reset,
    error: mutation.error
  };
}

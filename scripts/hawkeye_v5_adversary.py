#!/usr/bin/env python3
"""
Hawkeye v5.0 Adversarial Consent Processor Runner
Simulates a pedantic Dunedin City Council building consent officer (Aimee Moylan / Mike Fay).
Queries local LLMs (DeepSeek-R1 / Llama-3) via Ollama/vLLM on the ATOM to predict RFIs.
"""

import os
import sys
import json
import urllib.request
import urllib.error

class HawkeyeAdversaryRunner:
    def __init__(self, api_url: str = "http://localhost:8000/v1/chat/completions", model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-FP8"):
        self.api_url = api_url
        self.model_name = model_name
        
    def query_local_llm(self, system_instruction: str, user_content: str) -> str:
        """
        Sends a request to the local vLLM instance running on the ATOM (OpenAI-compatible endpoint).
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1,
            "max_tokens": 4096
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.api_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                # Extract message content from OpenAI structure
                choices = res.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
                return "Error: Empty response from model."
        except urllib.error.URLError as e:
            return f"Error: Local vLLM service at {self.api_url} is not responding. (Details: {e.reason})"

    def run_adversarial_audit(self, project_name: str, fact_graph_data: dict, compliance_results: list, target_bca: str = "Dunedin City Council") -> str:
        """
        Constructs the adversarial prompt simulating a pedantic Building Consent Officer at the target BCA.
        """
        system_instruction = (
            f"You are a Senior Building Consent Officer at the {target_bca}.\n"
            f"Your job is to review Building Consent applications for the {target_bca} and protect homes from structural failure, weathertightness disasters, and energy efficiency omissions under the NZBC.\n"
            "You are extremely pedantic and search for any minor drafting error, product mismatch, or compliance omission to stop the processing clock.\n"
            "If any dimension, product brand, specification details, or engineering calculations mismatch between documents, you MUST halt the clock.\n"
            "Use specific New Zealand Building Code (NZBC) clauses, NZS 3604 standards, and AS/NZS 3500.2 standards to support your requests.\n\n"
            f"PROJECT: {project_name}\n"
            f"JURISDICTION: {target_bca}\n"
            "=========================================\n"
        )
        
        context = (
            "Here is the project fact graph extracted from Drawings, Specs, and Engineering:\n"
            f"{json.dumps(fact_graph_data, indent=2)}\n\n"
            "Here are the preliminary rule compliance checks:\n"
            f"{json.dumps(compliance_results, indent=2)}\n\n"
            "Write the formal Request for Information (RFI) letter. Break it down strictly by: \n"
            "1. Item Number\n"
            "2. BCA Request (be specific, quote matching/conflicting drawings or specifications)\n"
            "3. NZBC Clause / NZS 3604 or AS/NZS 3500 Standard reference\n"
            "4. Required response action to restart the processing clock.\n"
        )
        
        return self.query_local_llm(system_instruction, context)

if __name__ == "__main__":
    # Test query using dummy data
    runner = HawkeyeAdversaryRunner(model_name="llama3:latest") # fallback model for testing
    
    dummy_graph = {
        "sheets": {
            "301": "Foundation Plan - Footing Depth = 300mm",
            "702": "Deck Detail - Waterproofing = Ardex WPM 195, slope 1.0 deg"
        },
        "specifications": {
            "0421": "Waterproofing: Ardex WPM 5000"
        },
        "engineering": {
            "footing_depth_req": "600mm"
        }
    }
    
    dummy_compliance = [
        {"assertion": "Footing Depth Check", "status": "FAIL", "message": "Footing depth shown is 300mm; Geotech specifies 600mm."},
        {"assertion": "Deck Slope Check", "status": "FAIL", "message": "Slope shown is 1.0 deg; E2/AS1 requires 1.5 deg minimum."}
    ]
    
    print("Simulating adversarial DCC processing on local LLM...")
    rfi_letter = runner.run_adversarial_audit("675 Portobello Road Alterations", dummy_graph, dummy_compliance)
    print("\n=== Predicted DCC RFI Letter ===\n")
    print(rfi_letter)

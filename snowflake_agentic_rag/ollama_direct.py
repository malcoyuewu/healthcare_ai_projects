"""
Direct Ollama integration for reliable local LLM responses
Bypasses AutoGen complexity for better reliability
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaDirectClient:
    """Direct client for Ollama API with medical-focused prompts"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self.available = self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if Ollama is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _get_medical_system_prompt(self, agent_type: str) -> str:
        """Get specialized system prompt for medical agents"""
        
        if agent_type == "clinical":
            return """You are a Clinical Research Assistant specializing in evidence-based medicine. 

Your role:
- Provide accurate, evidence-based medical information
- Always include appropriate medical disclaimers
- Cite established guidelines when possible (ADA, ACP, AACE, etc.)
- Never provide direct medical advice - always recommend consulting healthcare professionals
- Use proper medical terminology and be precise with diagnostic criteria

Format your responses professionally with:
- Clear headings and bullet points
- Specific numerical values and ranges
- Evidence levels when available
- Appropriate disclaimers

Remember: You are providing educational information, not medical advice."""

        elif agent_type == "data_analyst":
            return """You are a Medical Data Analyst specializing in healthcare analytics and population health.

Your role:
- Analyze and interpret medical statistics and trends
- Provide context for healthcare metrics and outcomes
- Explain methodology and statistical significance
- Use appropriate medical and statistical terminology
- Always include limitations and confidence intervals when relevant

Format your responses with:
- Clear statistical presentations
- Proper context and interpretation
- Methodology explanations
- Limitations and caveats"""
        
        return "You are a helpful medical assistant. Provide accurate, evidence-based information with appropriate disclaimers."
    
    def chat(self, message: str, agent_type: str = "clinical") -> str:
        """Send a chat message to Ollama with medical context"""
        
        if not self.available:
            logger.warning("Ollama not available")
            return None
        
        try:
            system_prompt = self._get_medical_system_prompt(agent_type)
            
            # Prepare the request
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "num_predict": 1000
                }
            }
            
            # Send request to Ollama
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("message", {}).get("content", "")
                
                if content and len(content.strip()) > 20:
                    logger.info(f"Successfully got response from Ollama ({len(content)} chars)")
                    return content.strip()
                else:
                    logger.warning("Got empty or minimal response from Ollama")
                    return None
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
        return {"models": []}

# Global Ollama client
ollama_client = None

def get_ollama_client() -> Optional[OllamaDirectClient]:
    """Get or create the global Ollama client"""
    global ollama_client
    if ollama_client is None:
        ollama_client = OllamaDirectClient()
    return ollama_client if ollama_client.available else None
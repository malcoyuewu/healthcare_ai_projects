import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import autogen
from autogen import AssistantAgent, UserProxyAgent, register_function

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthcareAgentConfig:
    """Configuration for healthcare agentic system using multiple LLMs with fallback"""
    
    def __init__(self):
        self.config_list = self._build_config_list_with_fallback()
        self.llm_config = {
            "config_list": self.config_list,
            "cache_seed": 42,
            "temperature": 0.1,
            "timeout": 120,
        }
    
    def _test_ollama_availability(self) -> bool:
        """Test if Ollama is available locally"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _build_config_list_with_fallback(self) -> List[Dict[str, Any]]:
        """Build configuration list with Ollama as primary fallback"""
        config_list = []
        
        # Check Ollama availability first (most reliable)
        ollama_available = self._test_ollama_availability()
        if ollama_available:
            logger.info("Ollama detected and available - adding as primary option")
            config_list.append({
                "model": "mistral",  # Use the actual model we have
                "base_url": "http://localhost:11434/v1",
                "api_key": "ollama",  # Placeholder
                "api_type": "openai",  # Ollama uses OpenAI-compatible API
            })
        
        # Add cloud providers as secondary options
        cloud_providers = []
        
        # DeepSeek (usually most reliable cloud option)
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            cloud_providers.append({
                "model": "deepseek-chat",
                "api_key": deepseek_key,
                "base_url": "https://api.deepseek.com/v1",
            })
        
        # OpenAI GPT-4 (but use more reliable model)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.startswith("sk-"):
            cloud_providers.append({
                "model": "gpt-4o-mini",  # Use a more reliable/cheaper model
                "api_key": openai_key,
            })
        
        # Add cloud providers after Ollama
        config_list.extend(cloud_providers)
        
        # Fallback: Add Ollama even if not detected (in case it starts later)
        if not ollama_available:
            logger.warning("Ollama not detected - adding as fallback option")
            config_list.append({
                "model": "mistral",  # Use the actual model we have
                "base_url": "http://localhost:11434/v1", 
                "api_key": "ollama",
                "api_type": "openai",
            })
        
        if not config_list:
            raise ValueError("No LLM providers available. Please install Ollama or configure API keys.")
        
        logger.info(f"Configured {len(config_list)} LLM providers with fallback priority")
        for i, config in enumerate(config_list):
            model_name = config.get('model', 'Unknown')
            provider = "Ollama (Local)" if "localhost" in config.get('base_url', '') else "Cloud API"
            logger.info(f"  {i+1}. {model_name} ({provider})")
        
        return config_list

class HealthcareAgentSystem:
    """Healthcare agentic system with robust error handling and fallback"""
    
    def __init__(self):
        self.config = HealthcareAgentConfig()
        self.agents = self._create_agents()
        self._register_functions()
    
    def _create_agents(self) -> Dict[str, Any]:
        """Create specialized healthcare agents with error handling"""
        
        # Enhanced system messages with fallback instructions
        clinical_system_message = """You are a Clinical Research Assistant specializing in evidence-based medicine.

Your capabilities:
1. Search medical documents and guidelines using 'medical_document_search'
2. Analyze structured medical data using 'medical_data_analysis'

Guidelines:
- Always search for evidence before making recommendations
- Cite sources and evidence levels when available
- Distinguish between clinical guidelines and research data
- Provide balanced, evidence-based responses
- Ask for clarification if the medical question is ambiguous
- Never provide direct medical advice - always recommend consulting healthcare professionals

IMPORTANT: If you encounter API errors or connection issues, continue with your medical knowledge 
and clearly state that some real-time data may not be available.

When responding:
1. First search relevant medical literature/guidelines
2. Analyze any relevant structured data if needed
3. Synthesize findings with proper citations
4. Include appropriate medical disclaimers"""

        data_analyst_system_message = """You are a Medical Data Analyst specializing in healthcare analytics and population health.

Your capabilities:
1. Analyze medical statistics and trends using 'medical_data_analysis'
2. Search supporting documentation using 'medical_document_search'

Focus areas:
- Patient outcome analysis
- Treatment effectiveness metrics
- Population health trends
- Healthcare quality indicators
- Clinical performance metrics

IMPORTANT: If database connections fail, use your analytical knowledge to provide 
general guidance and clearly indicate when real-time data is unavailable.

Always:
- Provide statistical context and confidence intervals when available
- Explain methodology and limitations
- Use appropriate medical terminology
- Suggest additional analyses when relevant"""
        
        # Clinical Research Assistant
        clinical_assistant = AssistantAgent(
            name="Clinical_Researcher",
            system_message=clinical_system_message,
            llm_config=self.config.llm_config,
        )
        
        # Medical Data Analyst
        data_analyst = AssistantAgent(
            name="Medical_Data_Analyst", 
            system_message=data_analyst_system_message,
            llm_config=self.config.llm_config,
        )
        
        # User Proxy for function execution
        user_proxy = UserProxyAgent(
            name="Medical_Admin",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,
        )
        
        return {
            "clinical_assistant": clinical_assistant,
            "data_analyst": data_analyst,
            "user_proxy": user_proxy
        }
    
    def _register_functions(self):
        """Register Snowflake search functions with agents"""
        from config_cortex_search import (
            medical_document_search, 
            medical_data_analysis
        )
        
        # Register document search function
        register_function(
            medical_document_search,
            caller=self.agents["clinical_assistant"],
            executor=self.agents["user_proxy"],
            name="medical_document_search",
            description="Search medical documents, guidelines, and policies in the knowledge base"
        )
        
        register_function(
            medical_document_search,
            caller=self.agents["data_analyst"],
            executor=self.agents["user_proxy"],
            name="medical_document_search",
            description="Search medical documents for context and supporting information"
        )
        
        # Register data analysis function
        register_function(
            medical_data_analysis,
            caller=self.agents["clinical_assistant"],
            executor=self.agents["user_proxy"],
            name="medical_data_analysis",
            description="Query and analyze structured medical data and statistics"
        )
        
        register_function(
            medical_data_analysis,
            caller=self.agents["data_analyst"],
            executor=self.agents["user_proxy"],
            name="medical_data_analysis",
            description="Perform statistical analysis on medical data and metrics"
        )
    
    def _safe_chat(self, agent_name: str, message: str) -> str:
        """Safely execute chat with comprehensive error handling"""
        
        # First, try direct Ollama if available (more reliable)
        try:
            from ollama_direct import get_ollama_client
            ollama_client = get_ollama_client()
            
            if ollama_client:
                logger.info(f"Trying direct Ollama for {agent_name}")
                agent_type = "clinical" if "clinical" in agent_name else "data_analyst"
                ollama_response = ollama_client.chat(message, agent_type)
                
                if ollama_response and len(ollama_response.strip()) > 50:
                    logger.info(f"Successfully got response from direct Ollama")
                    return ollama_response
                else:
                    logger.warning("Direct Ollama gave empty response, trying AutoGen")
        except Exception as e:
            logger.warning(f"Direct Ollama failed: {e}, trying AutoGen")
        
        # Fallback to AutoGen with retries
        max_retries = 2  # Reduced retries since we have Ollama fallback
        
        for attempt in range(max_retries):
            try:
                agent = self.agents[agent_name]
                user_proxy = self.agents["user_proxy"]
                
                logger.info(f"AutoGen attempt {attempt + 1}: Trying {agent_name} chat")
                
                # Try the chat with timeout
                chat_result = user_proxy.initiate_chat(
                    agent,
                    message=message,
                    silent=True,
                    max_turns=2  # Reduced turns for faster failure
                )
                
                response = self._extract_final_response(chat_result)
                
                # Check if we got a meaningful response
                if response and len(response.strip()) > 50 and "No response generated" not in response:
                    logger.info(f"Successfully got response from AutoGen {agent_name}")
                    return response
                else:
                    logger.warning(f"Got empty or minimal response from AutoGen {agent_name}")
                    if attempt < max_retries - 1:
                        continue
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"AutoGen attempt {attempt + 1} failed for {agent_name}: {error_msg}")
                
                # If this is the last attempt, continue to fallback
                if attempt == max_retries - 1:
                    break
                
                # Wait a bit before retrying
                import time
                time.sleep(1)
        
        # If all attempts failed, provide intelligent fallback
        logger.warning("All LLM attempts failed, using intelligent fallback")
        return self._generate_fallback_response(message, "GENERAL_ERROR")
    
    def _generate_fallback_response(self, message: str, error_type: str) -> str:
        """Generate helpful fallback responses when APIs fail"""
        
        base_disclaimer = "\n\n⚠️ **Note**: Real-time data access is currently limited due to API connectivity issues. This response is based on general medical knowledge."
        
        # Enhanced medical responses for common queries
        message_lower = message.lower()
        
        if "diabetes" in message_lower and ("criteria" in message_lower or "criterion" in message_lower or "diagnosis" in message_lower):
            return f"""**Type 2 Diabetes Diagnostic Criteria (ADA Guidelines):**

**Any ONE of the following criteria is sufficient for diagnosis:**

1. **Fasting Plasma Glucose (FPG)**: ≥126 mg/dL (7.0 mmol/L)
   - Fasting defined as no caloric intake for at least 8 hours

2. **2-Hour Plasma Glucose**: ≥200 mg/dL (11.1 mmol/L) during 75-g oral glucose tolerance test (OGTT)

3. **Hemoglobin A1C**: ≥6.5% (48 mmol/mol)
   - Test should be performed using NGSP-certified method
   - Standardized to DCCT assay

4. **Random Plasma Glucose**: ≥200 mg/dL (11.1 mmol/L) 
   - In patients with classic hyperglycemic symptoms or hyperglycemic crisis

**Prediabetes Criteria:**
- **Fasting glucose**: 100-125 mg/dL (5.6-6.9 mmol/L)
- **2-hour OGTT**: 140-199 mg/dL (7.8-11.0 mmol/L)  
- **A1C**: 5.7-6.4% (39-47 mmol/mol)

**Important Notes:**
- In absence of unequivocal hyperglycemia, results should be confirmed by repeat testing
- Different tests may not be concordant; clinical judgment is required

{base_disclaimer}

**Source**: American Diabetes Association Standards of Medical Care"""
        
        elif "diabetes" in message_lower and ("symptom" in message_lower or "sign" in message_lower):
            return f"""**Type 2 Diabetes Symptoms:**

**Classic Symptoms:**
- **Polyuria** (frequent urination)
- **Polydipsia** (excessive thirst)
- **Polyphagia** (increased hunger)
- **Unexplained weight loss**

**Additional Symptoms:**
- Fatigue and weakness
- Blurred vision
- Slow-healing wounds
- Frequent infections (especially skin, gum, bladder)
- Tingling or numbness in hands/feet
- Dry skin
- Recurrent yeast infections

**Acute Complications:**
- Diabetic ketoacidosis (rare in Type 2)
- Hyperosmolar hyperglycemic state
- Severe dehydration

**Note**: Many people with Type 2 diabetes are asymptomatic, especially in early stages. Regular screening is important for at-risk populations.

{base_disclaimer}"""
        
        elif "metformin" in message_lower and ("side effect" in message_lower or "adverse" in message_lower):
            return f"""**Metformin Side Effects:**

**Common Side Effects (>10%):**
- Gastrointestinal: Diarrhea, nausea, vomiting, abdominal pain, flatulence
- Metallic taste
- Decreased appetite

**Less Common Side Effects (1-10%):**
- Vitamin B12 deficiency (long-term use)
- Lactic acidosis (rare but serious)
- Hypoglycemia (when combined with other antidiabetic agents)

**Contraindications:**
- Severe kidney disease (eGFR <30 mL/min/1.73m²)
- Acute or chronic metabolic acidosis
- Severe heart failure
- Severe liver disease
- Acute illness with risk of tissue hypoxia

**Monitoring:**
- Kidney function (eGFR) before initiation and periodically
- Vitamin B12 levels annually
- Liver function tests if indicated

{base_disclaimer}"""
        
        elif "hypertension" in message_lower and "diabetes" in message_lower:
            return f"""**Hypertension Management in Diabetes:**

**Blood Pressure Targets:**
- **General target**: <130/80 mmHg for most adults with diabetes
- **Higher risk patients**: May benefit from <130/80 mmHg
- **Individualize** based on cardiovascular risk, life expectancy, comorbidities

**First-Line Medications:**
1. **ACE inhibitors** or **ARBs** (preferred for diabetic nephropathy)
2. **Thiazide or thiazide-like diuretics**
3. **Calcium channel blockers**

**Combination Therapy:**
- Often required to achieve target BP
- ACE inhibitor/ARB + diuretic commonly used
- Avoid ACE inhibitor + ARB combination

**Lifestyle Modifications:**
- DASH diet, sodium restriction (<2300 mg/day)
- Weight loss if overweight
- Regular physical activity
- Limit alcohol consumption
- Smoking cessation

{base_disclaimer}"""
        
        # Default responses for other queries
        elif error_type == "API_ERROR":
            return f"""I'm currently unable to access real-time medical databases due to API connectivity issues.

**For your question about**: {message[:100]}...

**Recommended Actions:**
1. Consult current clinical guidelines from reputable sources (ADA, ACP, AACE)
2. Check recent peer-reviewed literature (PubMed, Cochrane)
3. Verify with healthcare professionals
4. Use established medical references (UpToDate, Lexicomp)

{base_disclaimer}"""
        
        elif error_type == "CONNECTION_ERROR":
            return f"""I'm currently unable to access real-time medical databases due to connectivity issues.

**For your question about**: {message[:100]}...

**Recommended Actions:**
1. Consult current clinical guidelines from reputable sources
2. Check recent peer-reviewed literature
3. Verify with healthcare professionals
4. Use established medical references

{base_disclaimer}"""
        
        # Default fallback
        return f"""I apologize, but I'm currently experiencing technical difficulties accessing medical databases.

**For medical questions**, please:
- Consult current clinical practice guidelines
- Review peer-reviewed medical literature  
- Verify information with healthcare professionals
- Use established medical reference sources

{base_disclaimer}

**Your question**: {message[:200]}{'...' if len(message) > 200 else ''}"""
    
    def chat_with_clinical_assistant(self, message: str) -> str:
        """Start a chat with the clinical research assistant"""
        return self._safe_chat("clinical_assistant", message)
    
    def chat_with_data_analyst(self, message: str) -> str:
        """Start a chat with the medical data analyst"""
        return self._safe_chat("data_analyst", message)
    
    def _extract_final_response(self, chat_result) -> str:
        """Extract the final response from chat result"""
        try:
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                # Get the last assistant message
                for message in reversed(chat_result.chat_history):
                    if message.get('role') == 'assistant':
                        return message.get('content', 'No response generated')
            return "No response generated"
        except Exception as e:
            logger.error(f"Error extracting response: {e}")
            return "Error processing response"

# Global healthcare agent system
healthcare_system = None

def get_healthcare_system() -> HealthcareAgentSystem:
    """Get or create the global healthcare agent system"""
    global healthcare_system
    if healthcare_system is None:
        healthcare_system = HealthcareAgentSystem()
    return healthcare_system
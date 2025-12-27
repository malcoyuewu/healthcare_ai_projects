"""
Streamlit-optimized Healthcare Agentic System
Designed to work with Streamlit's caching and session management
"""

import os
import logging
import streamlit as st
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamlitHealthcareSystem:
    """Streamlit-optimized healthcare agentic system"""
    
    def __init__(self):
        self.snowflake_connector = None
        self.healthcare_system = None
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the healthcare system components"""
        try:
            # Initialize Snowflake connector
            from config_cortex_search import SnowflakeConnector
            self.snowflake_connector = SnowflakeConnector()
            
            # Initialize AutoGen system
            from autogen_configs import get_healthcare_system
            self.healthcare_system = get_healthcare_system()
            
            logger.info("Healthcare system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize healthcare system: {e}")
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            'snowflake_connected': False,
            'agents_initialized': False,
            'available_llms': 0,
            'error_message': None
        }
        
        try:
            # Check Snowflake connection
            if self.snowflake_connector and self.snowflake_connector.session:
                self.snowflake_connector.session.sql("SELECT 1").collect()
                status['snowflake_connected'] = True
            
            # Check agents
            if self.healthcare_system:
                status['agents_initialized'] = True
                status['available_llms'] = len(self.healthcare_system.config.config_list)
            
        except Exception as e:
            status['error_message'] = str(e)
            logger.error(f"System status check failed: {e}")
        
        return status
    
    def search_documents(self, query: str, limit: int = 5) -> str:
        """Search medical documents"""
        if not self.snowflake_connector:
            return "Snowflake connector not available"
        
        try:
            return self.snowflake_connector.search_documents(query, limit)
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return f"Document search failed: {str(e)}"
    
    def analyze_data(self, question: str) -> str:
        """Analyze structured medical data"""
        if not self.snowflake_connector:
            return "Snowflake connector not available"
        
        try:
            return self.snowflake_connector.query_structured_data(question)
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            return f"Data analysis failed: {str(e)}"
    
    def chat_with_clinical_assistant(self, message: str) -> str:
        """Chat with clinical research assistant"""
        if not self.healthcare_system:
            return "Healthcare system not available"
        
        try:
            return self.healthcare_system.chat_with_clinical_assistant(message)
        except Exception as e:
            logger.error(f"Clinical assistant chat failed: {e}")
            return f"Clinical assistant error: {str(e)}"
    
    def chat_with_data_analyst(self, message: str) -> str:
        """Chat with medical data analyst"""
        if not self.healthcare_system:
            return "Healthcare system not available"
        
        try:
            return self.healthcare_system.chat_with_data_analyst(message)
        except Exception as e:
            logger.error(f"Data analyst chat failed: {e}")
            return f"Data analyst error: {str(e)}"
    
    def get_agent_info(self) -> List[Dict[str, Any]]:
        """Get information about available agents"""
        return [
            {
                "id": "clinical",
                "name": "Clinical Research Assistant",
                "icon": "👨‍⚕️",
                "description": "Specializes in medical guidelines, research, and evidence-based recommendations",
                "capabilities": [
                    "Medical literature search",
                    "Evidence synthesis", 
                    "Clinical guidelines interpretation",
                    "Drug information lookup",
                    "Treatment protocol guidance"
                ],
                "use_cases": [
                    "What are the current guidelines for diabetes screening?",
                    "What are the side effects of metformin?",
                    "How should I manage hypertension in diabetic patients?"
                ]
            },
            {
                "id": "data_analyst",
                "name": "Medical Data Analyst",
                "icon": "📊",
                "description": "Specializes in healthcare analytics, statistics, and trend analysis",
                "capabilities": [
                    "Statistical analysis",
                    "Trend identification",
                    "Outcome metrics calculation",
                    "Population health analysis",
                    "Performance benchmarking"
                ],
                "use_cases": [
                    "What is our patient satisfaction rate?",
                    "Show me HbA1c trends over the past year",
                    "Analyze readmission rates by department"
                ]
            }
        ]
    
    def close(self):
        """Clean up resources"""
        if self.snowflake_connector:
            self.snowflake_connector.close()

# Streamlit-specific functions for caching
@st.cache_resource
def get_streamlit_healthcare_system():
    """Get cached healthcare system instance"""
    return StreamlitHealthcareSystem()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_system_status():
    """Get cached system status"""
    system = get_streamlit_healthcare_system()
    return system.get_system_status()

@st.cache_data
def get_agent_information():
    """Get cached agent information"""
    system = get_streamlit_healthcare_system()
    return system.get_agent_info()

# Session state management
def initialize_streamlit_session():
    """Initialize Streamlit session state for healthcare app"""
    
    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Selected agent
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = 'clinical'
    
    # System metrics
    if 'session_metrics' not in st.session_state:
        st.session_state.session_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'session_start_time': None
        }
    
    # User preferences
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'show_sources': True,
            'detailed_responses': True,
            'auto_scroll': True
        }

def add_to_chat_history(query: str, response: str, agent_type: str, success: bool = True, processing_time: float = 0):
    """Add interaction to chat history"""
    from datetime import datetime
    
    chat_entry = {
        'timestamp': datetime.now(),
        'query': query,
        'response': response,
        'agent_type': agent_type,
        'success': success,
        'processing_time': processing_time
    }
    
    st.session_state.chat_history.append(chat_entry)
    
    # Update metrics
    st.session_state.session_metrics['total_queries'] += 1
    if success:
        st.session_state.session_metrics['successful_queries'] += 1
    else:
        st.session_state.session_metrics['failed_queries'] += 1
    
    # Limit chat history size
    max_history = 50
    if len(st.session_state.chat_history) > max_history:
        st.session_state.chat_history = st.session_state.chat_history[-max_history:]

def clear_chat_history():
    """Clear chat history and reset metrics"""
    st.session_state.chat_history = []
    st.session_state.session_metrics = {
        'total_queries': 0,
        'successful_queries': 0,
        'failed_queries': 0,
        'session_start_time': st.session_state.session_metrics.get('session_start_time')
    }

def export_chat_history() -> str:
    """Export chat history as formatted text"""
    if not st.session_state.chat_history:
        return "No chat history to export."
    
    export_text = "Healthcare AI Assistant - Chat History Export\n"
    export_text += "=" * 50 + "\n\n"
    
    for i, chat in enumerate(st.session_state.chat_history, 1):
        export_text += f"Query {i} ({chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})\n"
        export_text += f"Agent: {chat['agent_type'].replace('_', ' ').title()}\n"
        export_text += f"Question: {chat['query']}\n"
        export_text += f"Response: {chat['response']}\n"
        export_text += f"Success: {chat['success']}\n"
        export_text += f"Processing Time: {chat['processing_time']:.2f}s\n"
        export_text += "-" * 30 + "\n\n"
    
    return export_text
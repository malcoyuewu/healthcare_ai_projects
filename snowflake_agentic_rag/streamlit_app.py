"""
Healthcare Agentic RAG System - Streamlit Home Page
Main dashboard and system overview
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from streamlit_healthcare_system import (
    get_streamlit_healthcare_system,
    initialize_streamlit_session,
    get_cached_system_status,
    get_agent_information
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Healthcare Agentic RAG System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session
initialize_streamlit_session()

# Custom CSS for healthcare theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2c3e50 0%, #3498db 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
        height: 200px;
    }
    
    .agent-preview {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .status-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-highlight {
        font-size: 2em;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .quick-action {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .quick-action:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Healthcare Agentic RAG System</h1>
        <p style="font-size: 1.2em; margin: 0;">
            AI-Powered Medical Knowledge Search & Analysis Platform
        </p>
        <p style="font-size: 1em; margin-top: 0.5rem; opacity: 0.9;">
            Powered by Snowflake Cortex AI & AutoGen Multi-Agent Framework
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_system_overview():
    """Display system status overview"""
    st.markdown("## 🔍 System Overview")
    
    try:
        status = get_cached_system_status()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            snowflake_icon = "🟢" if status['snowflake_connected'] else "🔴"
            st.markdown(f"""
            <div class="status-card">
                <div style="font-size: 2em;">{snowflake_icon}</div>
                <strong>Snowflake</strong><br>
                {'Connected' if status['snowflake_connected'] else 'Disconnected'}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            agents_icon = "🟢" if status['agents_initialized'] else "🔴"
            st.markdown(f"""
            <div class="status-card">
                <div style="font-size: 2em;">{agents_icon}</div>
                <strong>AI Agents</strong><br>
                {'Ready' if status['agents_initialized'] else 'Error'}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-highlight">{status['available_llms']}</div>
                <strong>LLM Providers</strong><br>
                Available
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            session_queries = st.session_state.session_metrics['total_queries']
            st.markdown(f"""
            <div class="status-card">
                <div class="metric-highlight">{session_queries}</div>
                <strong>Session Queries</strong><br>
                This Session
            </div>
            """, unsafe_allow_html=True)
        
        # Overall status
        if status['snowflake_connected'] and status['agents_initialized']:
            st.success("✅ All systems operational and ready for medical queries")
        elif status['snowflake_connected'] or status['agents_initialized']:
            st.warning("⚠️ Partial system availability - some features may be limited")
        else:
            st.error("❌ System issues detected - please check configuration")
        
        if status.get('error_message'):
            st.error(f"System Error: {status['error_message']}")
    
    except Exception as e:
        st.error(f"Failed to load system status: {e}")

def display_ai_agents():
    """Display AI agents overview"""
    st.markdown("## 🤖 AI Medical Assistants")
    
    try:
        agents = get_agent_information()
        
        col1, col2 = st.columns(2)
        
        for i, agent in enumerate(agents):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                st.markdown(f"""
                <div class="agent-preview">
                    <h3>{agent['icon']} {agent['name']}</h3>
                    <p>{agent['description']}</p>
                    <strong>Key Capabilities:</strong>
                    <ul>
                        {''.join([f"<li>{cap}</li>" for cap in agent['capabilities'][:3]])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🚀 Start Chat with {agent['name']}", key=f"start_{agent['id']}"):
                    st.session_state.selected_agent = agent['id']
                    st.switch_page("pages/1_🤖_AI_Assistant.py")
    
    except Exception as e:
        st.error(f"Failed to load agent information: {e}")

def display_features():
    """Display key features"""
    st.markdown("## ⭐ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔍 Intelligent Search</h4>
            <p>Hybrid vector + keyword search through medical documents, guidelines, and research papers with advanced filtering.</p>
            <ul>
                <li>Medical literature search</li>
                <li>Policy & procedure lookup</li>
                <li>Evidence-based results</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Data Analysis</h4>
            <p>Natural language queries on structured medical data with intelligent SQL generation and statistical analysis.</p>
            <ul>
                <li>Patient outcome metrics</li>
                <li>Treatment effectiveness</li>
                <li>Population health trends</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 Multi-Agent AI</h4>
            <p>Specialized medical AI assistants with domain expertise and evidence-based recommendations.</p>
            <ul>
                <li>Clinical research assistant</li>
                <li>Medical data analyst</li>
                <li>Evidence synthesis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_quick_actions():
    """Display quick action buttons"""
    st.markdown("## 🚀 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💬 Ask Clinical Question", use_container_width=True, type="primary"):
            st.session_state.selected_agent = 'clinical'
            st.switch_page("pages/1_🤖_AI_Assistant.py")
        
        if st.button("🔍 Search Medical Documents", use_container_width=True):
            st.switch_page("pages/2_🔍_Direct_Search.py")
    
    with col2:
        if st.button("📊 Analyze Medical Data", use_container_width=True, type="primary"):
            st.session_state.selected_agent = 'data_analyst'
            st.switch_page("pages/1_🤖_AI_Assistant.py")
        
        if st.button("📈 View System Analytics", use_container_width=True):
            st.switch_page("pages/3_📊_Analytics.py")

def display_example_queries():
    """Display example queries"""
    st.markdown("## 💡 Example Medical Queries")
    
    examples = [
        {
            "category": "Clinical Guidelines",
            "icon": "👨‍⚕️",
            "queries": [
                "What are the current guidelines for diabetes screening in adults?",
                "What is the recommended HbA1c target for elderly patients?",
                "How should I manage hypertension in diabetic patients?"
            ]
        },
        {
            "category": "Drug Information",
            "icon": "💊",
            "queries": [
                "What are the side effects of metformin?",
                "What are the contraindications for ACE inhibitors?",
                "What is the recommended dosing for insulin therapy?"
            ]
        },
        {
            "category": "Data Analysis",
            "icon": "📊",
            "queries": [
                "What is our patient satisfaction rate for diabetes care?",
                "Show me HbA1c trends over the past year",
                "Analyze readmission rates by department"
            ]
        }
    ]
    
    for example in examples:
        with st.expander(f"{example['icon']} {example['category']} Examples"):
            for query in example['queries']:
                if st.button(f"📝 {query}", key=f"example_{hash(query)}"):
                    st.session_state.example_query = query
                    st.switch_page("pages/1_🤖_AI_Assistant.py")

def display_medical_disclaimer():
    """Display medical disclaimer"""
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Medical Disclaimer:</strong> This AI system is designed for informational and research purposes only. 
        All medical recommendations should be verified with qualified healthcare professionals. 
        The AI assistants provide evidence-based information but do not replace clinical judgment or professional medical advice.
    </div>
    """, unsafe_allow_html=True)

def display_sidebar_info():
    """Display information in sidebar"""
    st.sidebar.markdown("## 📋 Navigation")
    st.sidebar.markdown("""
    **🤖 AI Assistant** - Chat with medical AI agents
    
    **🔍 Direct Search** - Search documents and analyze data
    
    **📊 Analytics** - View system metrics and usage stats
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ℹ️ System Info")
    
    # Display current time
    st.sidebar.markdown(f"**Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Session info
    if st.session_state.session_metrics['session_start_time']:
        start_time = st.session_state.session_metrics['session_start_time']
        duration = datetime.now() - start_time
        st.sidebar.markdown(f"**Session Duration:** {str(duration).split('.')[0]}")
    
    st.sidebar.markdown(f"**Total Queries:** {st.session_state.session_metrics['total_queries']}")
    
    # Quick settings
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ⚙️ Quick Settings")
    
    if st.sidebar.button("🔄 Refresh System Status"):
        st.cache_resource.clear()
        st.rerun()
    
    if st.sidebar.button("🗑️ Clear Session Data"):
        from streamlit_healthcare_system import clear_chat_history
        clear_chat_history()
        st.sidebar.success("Session data cleared!")

def main():
    """Main home page function"""
    # Sidebar info
    display_sidebar_info()
    
    # Main content
    display_header()
    
    # Medical disclaimer
    display_medical_disclaimer()
    
    # System overview
    display_system_overview()
    
    st.markdown("---")
    
    # AI agents overview
    display_ai_agents()
    
    st.markdown("---")
    
    # Key features
    display_features()
    
    st.markdown("---")
    
    # Quick actions
    display_quick_actions()
    
    st.markdown("---")
    
    # Example queries
    display_example_queries()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        Healthcare Agentic RAG System v1.0 | 
        Built with Streamlit, Snowflake Cortex AI & AutoGen | 
        <a href="https://github.com/your-repo" target="_blank">Documentation</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
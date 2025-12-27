"""
AI Assistant Page - Main chat interface with medical AI agents
"""

import streamlit as st
import time
from datetime import datetime
from streamlit_healthcare_system import (
    get_streamlit_healthcare_system,
    initialize_streamlit_session,
    add_to_chat_history,
    clear_chat_history
)

# Page configuration
st.set_page_config(
    page_title="AI Assistant - Healthcare RAG",
    page_icon="🤖",
    layout="wide"
)

# Initialize session
initialize_streamlit_session()

# Custom CSS
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def display_medical_disclaimer():
    """Display medical disclaimer"""
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Medical Disclaimer:</strong> This AI system is for informational and research purposes only. 
        All medical recommendations should be verified with qualified healthcare professionals. 
        The AI assistants provide evidence-based information but do not replace clinical judgment.
    </div>
    """, unsafe_allow_html=True)

def display_agent_selection():
    """Display agent selection interface"""
    st.sidebar.markdown("## 🤖 Select AI Assistant")
    
    # Get agent information
    try:
        system = get_streamlit_healthcare_system()
        agents = system.get_agent_info()
    except Exception as e:
        st.sidebar.error(f"Failed to load agent info: {e}")
        return None
    
    # Agent selection
    agent_options = {agent['id']: f"{agent['icon']} {agent['name']}" for agent in agents}
    
    selected_agent_id = st.sidebar.radio(
        "Choose your assistant:",
        options=list(agent_options.keys()),
        format_func=lambda x: agent_options[x],
        key='selected_agent_radio'
    )
    
    # Update session state
    st.session_state.selected_agent = selected_agent_id
    
    # Display agent details
    selected_agent = next(agent for agent in agents if agent['id'] == selected_agent_id)
    
    st.sidebar.markdown(f"### {selected_agent['icon']} {selected_agent['name']}")
    st.sidebar.markdown(f"**Description:** {selected_agent['description']}")
    
    st.sidebar.markdown("**Capabilities:**")
    for capability in selected_agent['capabilities']:
        st.sidebar.markdown(f"• {capability}")
    
    # Example queries
    st.sidebar.markdown("### 💡 Example Queries")
    for i, example in enumerate(selected_agent['use_cases']):
        if st.sidebar.button(f"📝 {example[:40]}...", key=f"example_{selected_agent_id}_{i}"):
            st.session_state.example_query = example
            st.rerun()
    
    return selected_agent

def process_query(system, query: str, agent_type: str):
    """Process a query with the selected agent"""
    start_time = time.time()
    
    try:
        if agent_type == 'clinical':
            response = system.chat_with_clinical_assistant(query)
            agent_name = "Clinical Research Assistant"
        else:
            response = system.chat_with_data_analyst(query)
            agent_name = "Medical Data Analyst"
        
        processing_time = time.time() - start_time
        
        # Add to chat history
        add_to_chat_history(
            query=query,
            response=response,
            agent_type=agent_type,
            success=True,
            processing_time=processing_time
        )
        
        return {
            'success': True,
            'response': response,
            'agent_name': agent_name,
            'processing_time': processing_time
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Error: {str(e)}"
        
        # Add error to chat history
        add_to_chat_history(
            query=query,
            response=error_msg,
            agent_type=agent_type,
            success=False,
            processing_time=processing_time
        )
        
        return {
            'success': False,
            'error': str(e),
            'processing_time': processing_time
        }

def display_chat_interface():
    """Display the main chat interface"""
    st.title("🤖 AI Medical Assistant")
    
    # Load system
    try:
        system = get_streamlit_healthcare_system()
        status = system.get_system_status()
    except Exception as e:
        st.error(f"❌ Failed to load healthcare system: {e}")
        st.info("💡 Please check your configuration and try again.")
        return
    
    # System status check
    if not status['agents_initialized']:
        st.error("❌ AI agents not available. Please check your configuration.")
        return
    
    if not status['snowflake_connected']:
        st.warning("⚠️ Snowflake connection issues. Some features may be limited.")
    
    # Medical disclaimer
    display_medical_disclaimer()
    
    # Query input section
    st.markdown("## 💬 Ask Your Medical Question")
    
    # Check for example query
    default_query = ""
    if hasattr(st.session_state, 'example_query'):
        default_query = st.session_state.example_query
        delattr(st.session_state, 'example_query')
    
    # Query input
    query = st.text_area(
        "Enter your medical question:",
        value=default_query,
        height=120,
        placeholder="e.g., What are the current guidelines for diabetes screening in adults?",
        help="Ask about medical guidelines, drug information, treatment protocols, or request data analysis."
    )
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        submit_button = st.button("🔍 Ask AI Assistant", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)
    
    with col3:
        export_button = st.button("📥 Export Chat", use_container_width=True)
    
    # Handle button actions
    if clear_button:
        clear_chat_history()
        st.success("Chat history cleared!")
        st.rerun()
    
    if export_button and st.session_state.chat_history:
        from streamlit_healthcare_system import export_chat_history
        export_text = export_chat_history()
        st.download_button(
            label="📄 Download Chat History",
            data=export_text,
            file_name=f"healthcare_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    # Process query
    if submit_button and query.strip():
        selected_agent = st.session_state.get('selected_agent', 'clinical')
        
        with st.spinner(f"🤖 {selected_agent.replace('_', ' ').title()} Assistant is thinking..."):
            result = process_query(system, query, selected_agent)
        
        if result['success']:
            st.success(f"✅ Response generated in {result['processing_time']:.2f} seconds")
        else:
            st.error(f"❌ Query failed: {result['error']}")
        
        st.rerun()

def display_chat_history():
    """Display chat history"""
    if not st.session_state.chat_history:
        st.info("💬 No conversation history yet. Ask a question to get started!")
        return
    
    st.markdown("## 📝 Conversation History")
    
    # Display recent conversations first
    for i, chat in enumerate(reversed(st.session_state.chat_history[-10:])):  # Show last 10
        chat_index = len(st.session_state.chat_history) - i
        
        with st.expander(
            f"💬 Query {chat_index}: {chat['query'][:80]}..." + 
            (" ✅" if chat['success'] else " ❌"), 
            expanded=(i == 0)
        ):
            # User query
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 You asked:</strong><br>
                {chat['query']}
            </div>
            """, unsafe_allow_html=True)
            
            # Agent response
            agent_name = chat['agent_type'].replace('_', ' ').title() + " Assistant"
            
            if chat['success']:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 {agent_name} responded:</strong><br>
                    <em>Processing time: {chat['processing_time']:.2f}s | {chat['timestamp'].strftime('%H:%M:%S')}</em>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(chat['response'])
            else:
                st.error(f"❌ {agent_name} Error: {chat['response']}")
            
            # Feedback buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Helpful", key=f"helpful_{chat_index}"):
                    st.success("Thank you for your feedback!")
            with col2:
                if st.button("👎 Not Helpful", key=f"not_helpful_{chat_index}"):
                    st.info("We'll work on improving our responses!")

def main():
    """Main page function"""
    # Agent selection in sidebar
    selected_agent = display_agent_selection()
    
    if not selected_agent:
        st.error("Failed to load AI agents. Please check your configuration.")
        return
    
    # Main chat interface
    display_chat_interface()
    
    # Chat history
    display_chat_history()
    
    # Session metrics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Session Stats")
    metrics = st.session_state.session_metrics
    st.sidebar.metric("Total Queries", metrics['total_queries'])
    st.sidebar.metric("Successful", metrics['successful_queries'])
    if metrics['total_queries'] > 0:
        success_rate = (metrics['successful_queries'] / metrics['total_queries']) * 100
        st.sidebar.metric("Success Rate", f"{success_rate:.1f}%")

if __name__ == "__main__":
    main()
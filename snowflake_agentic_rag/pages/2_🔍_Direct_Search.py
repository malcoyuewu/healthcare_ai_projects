"""
Direct Search Page - Direct access to document search and data analysis tools
"""

import streamlit as st
import time
import json
from datetime import datetime
from streamlit_healthcare_system import (
    get_streamlit_healthcare_system,
    initialize_streamlit_session
)

# Page configuration
st.set_page_config(
    page_title="Direct Search - Healthcare RAG",
    page_icon="🔍",
    layout="wide"
)

# Initialize session
initialize_streamlit_session()

# Custom CSS
st.markdown("""
<style>
    .search-result {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .result-header {
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .result-meta {
        font-size: 0.9em;
        color: #6c757d;
        margin-bottom: 0.5rem;
    }
    
    .result-content {
        background: white;
        padding: 0.8rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    
    .tool-card {
        background: #e3f2fd;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def display_document_search():
    """Display document search interface"""
    st.markdown("## 📄 Medical Document Search")
    
    st.markdown("""
    <div class="tool-card">
        <strong>🔍 Document Search Tool</strong><br>
        Search through medical documents, guidelines, policies, and research papers.
        Uses hybrid vector + keyword search for comprehensive results.
    </div>
    """, unsafe_allow_html=True)
    
    # Search parameters
    col1, col2 = st.columns([3, 1])
    
    with col1:
        doc_query = st.text_input(
            "Search Query:",
            placeholder="e.g., diabetes screening guidelines, metformin side effects",
            help="Enter keywords or phrases to search medical documents"
        )
    
    with col2:
        doc_limit = st.slider("Max Results:", 1, 20, 5)
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2 = st.columns(2)
        
        with col1:
            filter_department = st.selectbox(
                "Department Filter:",
                ["All", "Human Resources", "Engineering", "Sales", "Marketing"],
                help="Filter by document department"
            )
        
        with col2:
            filter_category = st.selectbox(
                "Category Filter:",
                ["All", "HR Policy", "Product Documentation", "Training Material", "General"],
                help="Filter by document category"
            )
    
    # Search button
    if st.button("🔍 Search Documents", type="primary"):
        if doc_query.strip():
            search_documents(doc_query, doc_limit, filter_department, filter_category)
        else:
            st.warning("Please enter a search query")

def search_documents(query: str, limit: int, department: str, category: str):
    """Execute document search"""
    try:
        system = get_streamlit_healthcare_system()
        
        with st.spinner("🔍 Searching medical documents..."):
            start_time = time.time()
            results = system.search_documents(query, limit)
            search_time = time.time() - start_time
        
        st.success(f"✅ Search completed in {search_time:.2f} seconds")
        
        # Display results
        st.markdown("### 📋 Search Results")
        
        if "No relevant medical information found" in results:
            st.info("🔍 No documents found matching your query. Try different keywords or broader terms.")
        else:
            # Parse and display results
            st.markdown(f"""
            <div class="search-result">
                <div class="result-header">Search Query: "{query}"</div>
                <div class="result-meta">Results: {limit} max | Time: {search_time:.2f}s</div>
                <div class="result-content">{results}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Download option
            st.download_button(
                label="📥 Download Results",
                data=f"Search Query: {query}\nTimestamp: {datetime.now()}\n\n{results}",
                file_name=f"document_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    except Exception as e:
        st.error(f"❌ Search failed: {str(e)}")

def display_data_analysis():
    """Display data analysis interface"""
    st.markdown("## 📊 Medical Data Analysis")
    
    st.markdown("""
    <div class="tool-card">
        <strong>📊 Data Analysis Tool</strong><br>
        Query and analyze structured medical data using natural language.
        Powered by Snowflake Cortex Analyst for intelligent SQL generation.
    </div>
    """, unsafe_allow_html=True)
    
    # Analysis parameters
    data_question = st.text_area(
        "Analysis Question:",
        height=100,
        placeholder="e.g., What is the average patient satisfaction score? Show me HbA1c trends by region.",
        help="Ask questions about medical metrics, trends, and statistics"
    )
    
    # Example questions
    st.markdown("### 💡 Example Analysis Questions")
    
    examples = [
        "What is our patient satisfaction rate for diabetes care?",
        "Show me HbA1c trends over the past year",
        "What is the average length of stay for cardiac patients?",
        "Analyze readmission rates by department",
        "What are the top 5 most prescribed medications?",
        "Show revenue by product category"
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(examples):
        col = cols[i % 2]
        with col:
            if st.button(f"📝 {example}", key=f"data_example_{i}"):
                st.session_state.data_question = example
                st.rerun()
    
    # Check for example selection
    if hasattr(st.session_state, 'data_question'):
        data_question = st.session_state.data_question
        delattr(st.session_state, 'data_question')
        st.rerun()
    
    # Analysis button
    if st.button("📊 Analyze Data", type="primary"):
        if data_question.strip():
            analyze_data(data_question)
        else:
            st.warning("Please enter an analysis question")

def analyze_data(question: str):
    """Execute data analysis"""
    try:
        system = get_streamlit_healthcare_system()
        
        with st.spinner("📊 Analyzing medical data..."):
            start_time = time.time()
            results = system.analyze_data(question)
            analysis_time = time.time() - start_time
        
        st.success(f"✅ Analysis completed in {analysis_time:.2f} seconds")
        
        # Display results
        st.markdown("### 📈 Analysis Results")
        
        st.markdown(f"""
        <div class="search-result">
            <div class="result-header">Analysis Question: "{question}"</div>
            <div class="result-meta">Processing time: {analysis_time:.2f}s</div>
            <div class="result-content">{results}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Try to parse JSON results for better display
        try:
            if results.startswith('{') or results.startswith('['):
                parsed_results = json.loads(results)
                st.json(parsed_results)
        except:
            pass  # Not JSON, display as text
        
        # Download option
        st.download_button(
            label="📥 Download Analysis",
            data=f"Analysis Question: {question}\nTimestamp: {datetime.now()}\n\n{results}",
            file_name=f"data_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")

def display_system_info():
    """Display system information in sidebar"""
    st.sidebar.markdown("## ℹ️ System Information")
    
    try:
        system = get_streamlit_healthcare_system()
        status = system.get_system_status()
        
        # Connection status
        snowflake_status = "🟢 Connected" if status['snowflake_connected'] else "🔴 Disconnected"
        st.sidebar.markdown(f"**Snowflake:** {snowflake_status}")
        
        agents_status = "🟢 Available" if status['agents_initialized'] else "🔴 Unavailable"
        st.sidebar.markdown(f"**AI Agents:** {agents_status}")
        
        if status['available_llms'] > 0:
            st.sidebar.markdown(f"**LLM Providers:** {status['available_llms']}")
        
        if status['error_message']:
            st.sidebar.error(f"Error: {status['error_message']}")
    
    except Exception as e:
        st.sidebar.error(f"System check failed: {e}")

def display_search_tips():
    """Display search tips and best practices"""
    st.sidebar.markdown("## 💡 Search Tips")
    
    st.sidebar.markdown("""
    **Document Search:**
    • Use specific medical terms
    • Include condition names
    • Try synonyms if no results
    • Use quotes for exact phrases
    
    **Data Analysis:**
    • Ask specific questions
    • Include time periods
    • Specify metrics clearly
    • Use comparative language
    """)

def main():
    """Main page function"""
    st.title("🔍 Direct Search Tools")
    
    st.markdown("""
    Access the underlying search and analysis tools directly. These are the same tools 
    used by the AI assistants, but with direct control over parameters and filters.
    """)
    
    # System info in sidebar
    display_system_info()
    display_search_tips()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📄 Document Search", "📊 Data Analysis"])
    
    with tab1:
        display_document_search()
    
    with tab2:
        display_data_analysis()
    
    # Usage statistics
    st.markdown("---")
    st.markdown("### 📊 Usage Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Session Queries", st.session_state.session_metrics['total_queries'])
    
    with col2:
        st.metric("Successful", st.session_state.session_metrics['successful_queries'])
    
    with col3:
        if st.session_state.session_metrics['total_queries'] > 0:
            success_rate = (st.session_state.session_metrics['successful_queries'] / 
                          st.session_state.session_metrics['total_queries']) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "N/A")

if __name__ == "__main__":
    main()
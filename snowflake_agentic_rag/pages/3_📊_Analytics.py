"""
Analytics Page - System metrics, usage statistics, and performance monitoring
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_healthcare_system import (
    get_streamlit_healthcare_system,
    initialize_streamlit_session
)

# Page configuration
st.set_page_config(
    page_title="Analytics - Healthcare RAG",
    page_icon="📊",
    layout="wide"
)

# Initialize session
initialize_streamlit_session()

def display_system_metrics():
    """Display real-time system metrics"""
    st.markdown("## 🔍 System Health Metrics")
    
    try:
        system = get_streamlit_healthcare_system()
        status = system.get_system_status()
        
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            snowflake_status = "Healthy" if status['snowflake_connected'] else "Issues"
            delta_color = "normal" if status['snowflake_connected'] else "inverse"
            st.metric(
                label="🏔️ Snowflake Status",
                value=snowflake_status,
                delta="Connected" if status['snowflake_connected'] else "Disconnected",
                delta_color=delta_color
            )
        
        with col2:
            agents_status = "Ready" if status['agents_initialized'] else "Error"
            delta_color = "normal" if status['agents_initialized'] else "inverse"
            st.metric(
                label="🤖 AI Agents",
                value=agents_status,
                delta="Available" if status['agents_initialized'] else "Unavailable",
                delta_color=delta_color
            )
        
        with col3:
            st.metric(
                label="🧠 LLM Providers",
                value=status['available_llms'],
                delta=f"{status['available_llms']} active"
            )
        
        with col4:
            # Calculate uptime (mock for demo)
            uptime = "99.9%"
            st.metric(
                label="⏱️ Uptime",
                value=uptime,
                delta="Last 24h"
            )
        
        # System status indicator
        if status['snowflake_connected'] and status['agents_initialized']:
            st.success("✅ All systems operational")
        elif status['snowflake_connected'] or status['agents_initialized']:
            st.warning("⚠️ Partial system availability")
        else:
            st.error("❌ System issues detected")
        
        if status['error_message']:
            st.error(f"System Error: {status['error_message']}")
    
    except Exception as e:
        st.error(f"Failed to load system metrics: {e}")

def display_usage_analytics():
    """Display usage analytics and statistics"""
    st.markdown("## 📈 Usage Analytics")
    
    # Session metrics
    metrics = st.session_state.session_metrics
    chat_history = st.session_state.chat_history
    
    if not chat_history:
        st.info("📊 No usage data available yet. Start using the AI assistant to see analytics!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Queries", metrics['total_queries'])
    
    with col2:
        st.metric("Successful Queries", metrics['successful_queries'])
    
    with col3:
        st.metric("Failed Queries", metrics['failed_queries'])
    
    with col4:
        if metrics['total_queries'] > 0:
            success_rate = (metrics['successful_queries'] / metrics['total_queries']) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Success Rate", "N/A")
    
    # Create analytics dataframe
    df_data = []
    for chat in chat_history:
        df_data.append({
            'timestamp': chat['timestamp'],
            'agent_type': chat['agent_type'],
            'success': chat['success'],
            'processing_time': chat['processing_time'],
            'query_length': len(chat['query']),
            'response_length': len(chat['response'])
        })
    
    if df_data:
        df = pd.DataFrame(df_data)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🤖 Queries by Agent Type")
            agent_counts = df['agent_type'].value_counts()
            fig_agents = px.pie(
                values=agent_counts.values,
                names=[name.replace('_', ' ').title() for name in agent_counts.index],
                title="Distribution of Agent Usage"
            )
            st.plotly_chart(fig_agents, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ Response Time Trends")
            fig_time = px.line(
                df,
                x='timestamp',
                y='processing_time',
                title="Response Time Over Time",
                labels={'processing_time': 'Response Time (seconds)'}
            )
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Success rate over time
        st.markdown("### ✅ Success Rate Analysis")
        
        # Group by hour for success rate calculation
        df['hour'] = df['timestamp'].dt.floor('H')
        hourly_stats = df.groupby('hour').agg({
            'success': ['count', 'sum'],
            'processing_time': 'mean'
        }).round(2)
        
        hourly_stats.columns = ['total_queries', 'successful_queries', 'avg_response_time']
        hourly_stats['success_rate'] = (hourly_stats['successful_queries'] / hourly_stats['total_queries'] * 100).round(1)
        
        if len(hourly_stats) > 1:
            fig_success = go.Figure()
            
            fig_success.add_trace(go.Scatter(
                x=hourly_stats.index,
                y=hourly_stats['success_rate'],
                mode='lines+markers',
                name='Success Rate (%)',
                line=dict(color='green')
            ))
            
            fig_success.update_layout(
                title="Success Rate Over Time",
                xaxis_title="Time",
                yaxis_title="Success Rate (%)",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig_success, use_container_width=True)
        
        # Performance metrics
        st.markdown("### ⚡ Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_response_time = df['processing_time'].mean()
            st.metric("Avg Response Time", f"{avg_response_time:.2f}s")
        
        with col2:
            fastest_response = df['processing_time'].min()
            st.metric("Fastest Response", f"{fastest_response:.2f}s")
        
        with col3:
            slowest_response = df['processing_time'].max()
            st.metric("Slowest Response", f"{slowest_response:.2f}s")

def display_query_analysis():
    """Display detailed query analysis"""
    st.markdown("## 🔍 Query Analysis")
    
    chat_history = st.session_state.chat_history
    
    if not chat_history:
        st.info("No queries to analyze yet.")
        return
    
    # Recent queries table
    st.markdown("### 📝 Recent Queries")
    
    # Prepare data for table
    table_data = []
    for i, chat in enumerate(reversed(chat_history[-10:])):  # Last 10 queries
        table_data.append({
            'Query #': len(chat_history) - i,
            'Timestamp': chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'Agent': chat['agent_type'].replace('_', ' ').title(),
            'Query': chat['query'][:100] + '...' if len(chat['query']) > 100 else chat['query'],
            'Success': '✅' if chat['success'] else '❌',
            'Response Time': f"{chat['processing_time']:.2f}s"
        })
    
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True)
    
    # Query statistics
    st.markdown("### 📊 Query Statistics")
    
    if chat_history:
        df = pd.DataFrame([{
            'query_length': len(chat['query']),
            'response_length': len(chat['response']),
            'processing_time': chat['processing_time'],
            'success': chat['success']
        } for chat in chat_history])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Query Length Distribution**")
            fig_query_len = px.histogram(
                df,
                x='query_length',
                title="Distribution of Query Lengths",
                labels={'query_length': 'Query Length (characters)'}
            )
            st.plotly_chart(fig_query_len, use_container_width=True)
        
        with col2:
            st.markdown("**Response Time vs Query Length**")
            fig_scatter = px.scatter(
                df,
                x='query_length',
                y='processing_time',
                color='success',
                title="Response Time vs Query Length",
                labels={
                    'query_length': 'Query Length (characters)',
                    'processing_time': 'Response Time (seconds)'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

def display_export_options():
    """Display data export options"""
    st.markdown("## 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics Data"):
            if st.session_state.chat_history:
                # Prepare analytics data
                analytics_data = []
                for chat in st.session_state.chat_history:
                    analytics_data.append({
                        'timestamp': chat['timestamp'],
                        'agent_type': chat['agent_type'],
                        'query': chat['query'],
                        'success': chat['success'],
                        'processing_time': chat['processing_time'],
                        'query_length': len(chat['query']),
                        'response_length': len(chat['response'])
                    })
                
                df = pd.DataFrame(analytics_data)
                csv_data = df.to_csv(index=False)
                
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"healthcare_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data to export")
    
    with col2:
        if st.button("💬 Export Chat History"):
            if st.session_state.chat_history:
                from streamlit_healthcare_system import export_chat_history
                chat_export = export_chat_history()
                
                st.download_button(
                    label="📄 Download Chat History",
                    data=chat_export,
                    file_name=f"healthcare_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            else:
                st.info("No chat history to export")
    
    with col3:
        if st.button("🔄 Reset All Data"):
            if st.button("⚠️ Confirm Reset", type="secondary"):
                from streamlit_healthcare_system import clear_chat_history
                clear_chat_history()
                st.success("All data has been reset!")
                st.rerun()

def main():
    """Main analytics page"""
    st.title("📊 System Analytics & Monitoring")
    
    st.markdown("""
    Monitor system performance, analyze usage patterns, and track the effectiveness 
    of your Healthcare Agentic RAG system.
    """)
    
    # System metrics
    display_system_metrics()
    
    st.markdown("---")
    
    # Usage analytics
    display_usage_analytics()
    
    st.markdown("---")
    
    # Query analysis
    display_query_analysis()
    
    st.markdown("---")
    
    # Export options
    display_export_options()
    
    # Auto-refresh option
    st.sidebar.markdown("## ⚙️ Settings")
    
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()
    
    # Manual refresh
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()

if __name__ == "__main__":
    main()
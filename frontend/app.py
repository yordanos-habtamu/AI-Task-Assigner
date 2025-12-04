"""
Streamlit Frontend for AI Task Assignment System
"""

import json
import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ai.graph import run_graph


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Task Assignment System",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Task Assignment System")
    st.markdown("""
    Upload your issues and developers data to get intelligent task assignments powered by AI.
    The system analyzes skills, workload, and preferences to make optimal assignments.
    """)
    
    # API Key input
    st.sidebar.header("⚙️ Configuration")
    
    # Try to get API key from environment first
    default_api_key = os.getenv("OPENAI_API_KEY", "")
    
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=default_api_key,
        type="password",
        help="Your OpenAI API key (auto-loaded from .env if available)"
    )
    
    if default_api_key:
        st.sidebar.success("✓ API key loaded from .env")
    
    # File uploaders
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Issues")
        uploaded_issues = st.file_uploader(
            "Upload issues JSON file",
            type=["json"],
            key="issues"
        )
        
        if uploaded_issues:
            try:
                issues_data = json.load(uploaded_issues)
                st.success(f"✓ Loaded {len(issues_data)} issues")
                
                with st.expander("Preview Issues"):
                    st.json(issues_data[:3] if len(issues_data) > 3 else issues_data)
            except json.JSONDecodeError:
                st.error("Invalid JSON file for issues")
                issues_data = None
        else:
            issues_data = None
    
    with col2:
        st.subheader("👥 Developers")
        uploaded_developers = st.file_uploader(
            "Upload developers JSON file",
            type=["json"],
            key="developers"
        )
        
        if uploaded_developers:
            try:
                developers_data = json.load(uploaded_developers)
                st.success(f"✓ Loaded {len(developers_data)} developers")
                
                with st.expander("Preview Developers"):
                    st.json(developers_data[:3] if len(developers_data) > 3 else developers_data)
            except json.JSONDecodeError:
                st.error("Invalid JSON file for developers")
                developers_data = None
        else:
            developers_data = None
    
    # Run button
    st.markdown("---")
    
    if st.button("🚀 Run AI Assignment", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please provide an OpenAI API key in the sidebar")
        elif not issues_data:
            st.error("Please upload an issues JSON file")
        elif not developers_data:
            st.error("Please upload a developers JSON file")
        else:
            with st.spinner("Running AI assignment workflow..."):
                try:
                    # Run the workflow
                    assignments = run_graph(issues_data, developers_data, api_key)
                    
                    # Store in session state
                    st.session_state.assignments = assignments
                    
                    st.success(f"✅ Successfully created {len(assignments)} assignments!")
                    
                except Exception as e:
                    st.error(f"Error running assignment: {str(e)}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
    
    # Display results
    if "assignments" in st.session_state and st.session_state.assignments:
        st.markdown("---")
        st.header("📊 Assignment Results")
        
        assignments = st.session_state.assignments
        
        # Create DataFrame for display
        df = pd.DataFrame(assignments)
        
        # Reorder columns for better display
        column_order = ['issue_id', 'developer_name', 'assigned_to', 'confidence_score', 'reason']
        df = df[column_order]
        
        # Rename columns for display
        df.columns = ['Issue ID', 'Developer Name', 'Developer ID', 'Confidence', 'Reason']
        
        # Display as table
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        # Download button
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # JSON download
            json_str = json.dumps(assignments, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name="assignments.json",
                mime="application/json"
            )
        
        with col2:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="assignments.csv",
                mime="text/csv"
            )
        
        # Assignment statistics
        st.markdown("---")
        st.subheader("📈 Statistics")
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.metric("Total Assignments", len(assignments))
        
        with stat_col2:
            avg_confidence = sum(a['confidence_score'] for a in assignments) / len(assignments)
            st.metric("Average Confidence", f"{avg_confidence:.1f}/10")
        
        with stat_col3:
            unique_devs = len(set(a['assigned_to'] for a in assignments))
            st.metric("Developers Assigned", unique_devs)


if __name__ == "__main__":
    main()

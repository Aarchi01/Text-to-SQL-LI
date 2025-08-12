import streamlit as st
from src.pipeline import ask_question
import time

# Set page config
st.set_page_config(
    page_title="Text-to-SQL Assistant",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if 'query_results' not in st.session_state:
    st.session_state.query_results = None
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

st.title("Natural Language to SQL Assistant")
st.markdown("Ask questions about your database in plain English!")

# Sidebar settings
with st.sidebar:
    st.markdown("### Settings")
    show_sql = st.checkbox("Show Generated SQL", value=False)
    show_reasoning = st.checkbox("Show LLM reasoning", value=False)
    show_schema = st.checkbox("Show full schema context", value=False)
    
    st.markdown("---")
    st.markdown("### Example Questions")
    st.code("""
• how many total hours have been worked on all projects per project?
• List all users assigned to project Essentia App.
• How many testers are in the company?
• Who is the most active user?
• how many departments are there and how many users are in each department?
    """)
    
    st.markdown("---")
    st.markdown("###  Tips")
    st.markdown("""
- Be specific in your questions
- Use proper names as they appear in database
- Ask one question at a time
    """)

# Main input area
st.markdown("### Ask your question:")

# Create columns for input and buttons
col1, col2, col3 = st.columns([6, 1, 1])

with col1:
    user_input = st.text_input(
        "Enter your question here...",
        value=st.session_state.user_input,
        label_visibility="collapsed"
    )

with col2:
    submit_clicked = st.button("Submit", type="primary", use_container_width=True)

with col3:
    clear_clicked = st.button("Clear", use_container_width=True)

# Handle clear button
if clear_clicked:
    st.session_state.user_input = ""
    st.session_state.query_results = None
    st.rerun()

# Handle submit button or Enter key
if submit_clicked or (user_input and user_input != st.session_state.user_input):
    if user_input.strip():
        st.session_state.user_input = user_input
        
        with st.spinner("Generating SQL and fetching answer..."):
            start = time.time()
            try:
                sql, answer, reasoning, schema = ask_question(
                    user_input, 
                    show_sql=show_sql,
                    show_reasoning=show_reasoning, 
                    show_schema=show_schema
                )
                latency = time.time() - start
                
                # Store results in session state
                st.session_state.query_results = {
                    'sql': sql,
                    'answer': answer,
                    'reasoning': reasoning,
                    'schema': schema,
                    'latency': latency,
                    'question': user_input
                }
                
            except Exception as e:
                st.error(f"Error processing your question: {str(e)}")
                st.session_state.query_results = None
    else:
        st.warning("Please enter a question before submitting.")

# Display results if available
if st.session_state.query_results:
    results = st.session_state.query_results
    
    # Create tabs for better organization
    if show_sql or show_reasoning or show_schema:
        tab1, tab2 = st.tabs(["Answer", "Technical Details"])
        
        with tab1:
            st.markdown("### Answer")
            st.success(results['answer'])
            st.markdown(f"⏱️*Response time: **{results['latency']:.2f} seconds***")
        
        with tab2:
            if show_sql and results['sql']:
                st.markdown("### Generated SQL")
                st.code(results['sql'], language="sql")
            
            if show_reasoning and results['reasoning']:
                st.markdown("### LLM Reasoning")
                st.text(results['reasoning'])
            
            if show_schema and results['schema']:
                st.markdown("### Schema Context")
                with st.expander("Click to view schema details"):
                    st.text(results['schema'])
    else:
        # Simple display when no technical details are shown
        st.markdown("### Answer")
        st.success(results['answer'])
        st.markdown(f"⏱️ *Response time: **{results['latency']:.2f} seconds***")
    

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        💡 Tip: Use the sidebar settings to see how your questions are processed!
    </div>
    """, 
    unsafe_allow_html=True
)


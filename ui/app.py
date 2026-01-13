"""
Streamlit UI for HR Copilot
"""
import sys
import os

# CRITICAL: Add parent directory to Python path so imports work
# This must be at the very top before any other imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
from datetime import datetime
from agents.orchestrator import orchestrator
from models.conversation import conversation_manager
from services.database_service import db_service
from config import settings, validate_settings


# Page config
st.set_page_config(
    page_title="HR Copilot",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session():
    """Initialize session state"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = conversation_manager.create_session()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'initialized' not in st.session_state:
        try:
            validate_settings()
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"⚠️ Configuration error: {str(e)}")
            st.session_state.initialized = False


def render_sidebar():
    """Render sidebar with navigation and info"""
    with st.sidebar:
        st.markdown("# 👔 HR Copilot")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigate",
            ["💬 Chat", "📊 Dashboard", "📋 Jobs", "👥 Candidates", "📅 Interviews"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### Quick Actions")
        if st.button("📝 Create Job Description"):
            st.session_state.quick_action = "create_jd"
        
        if st.button("📄 Screen Resume"):
            st.session_state.quick_action = "screen_resume"
        
        if st.button("📅 Schedule Interview"):
            st.session_state.quick_action = "schedule_interview"
        
        st.markdown("---")
        
        # Session info
        st.markdown("### Session Info")
        st.caption(f"Session: {st.session_state.session_id[:8]}...")
        st.caption(f"Messages: {len(st.session_state.messages)}")
        
        if st.button("🔄 New Session"):
            st.session_state.session_id = conversation_manager.create_session()
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.caption(f"HR Copilot v{settings.APP_VERSION}")
    
    return page


def render_chat_page():
    """Render chat interface"""
    st.markdown('<div class="main-header">HR Copilot Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your AI-powered hiring assistant</div>', unsafe_allow_html=True)
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            role = message['role']
            content = message['content']
            
            css_class = "user-message" if role == "user" else "assistant-message"
            icon = "🧑" if role == "user" else "🤖"
            
            st.markdown(
                f'<div class="chat-message {css_class}">{icon} <strong>{role.title()}:</strong><br>{content}</div>',
                unsafe_allow_html=True
            )
    
    # Chat input
    user_input = st.chat_input("Ask me anything about hiring...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get response from orchestrator
        with st.spinner("🤔 Thinking..."):
            try:
                response = orchestrator.process_request(
                    user_input,
                    st.session_state.session_id
                )
                
                # Add assistant message
                assistant_message = response.message
                
                # Add suggestions if any
                if response.suggestions:
                    assistant_message += "\n\n**Suggestions:**\n"
                    for suggestion in response.suggestions:
                        assistant_message += f"- {suggestion}\n"
                
                # Add next actions if any
                if response.next_actions:
                    assistant_message += "\n\n**Next Actions:**\n"
                    for action in response.next_actions:
                        assistant_message += f"✓ {action}\n"
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': assistant_message
                })
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': f"I encountered an error: {str(e)}"
                })
        
        st.rerun()


def render_dashboard():
    """Render analytics dashboard"""
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    # Get analytics
    analytics = db_service.get_analytics()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", analytics['total_jobs'])
    
    with col2:
        st.metric("Active Jobs", analytics['active_jobs'])
    
    with col3:
        st.metric("Total Candidates", analytics['total_candidates'])
    
    with col4:
        st.metric("Avg Match Score", f"{analytics['average_match_score']}%")
    
    st.markdown("---")
    
    # Candidates by status
    st.subheader("Candidates by Status")
    if analytics['candidates_by_status']:
        st.bar_chart(analytics['candidates_by_status'])
    else:
        st.info("No candidate data available yet")


def render_jobs_page():
    """Render jobs listing"""
    st.markdown('<div class="main-header">📋 Job Postings</div>', unsafe_allow_html=True)
    
    # Filter
    col1, col2 = st.columns([3, 1])
    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "draft", "active", "paused", "closed"]
        )
    
    # Get jobs
    jobs = db_service.list_jobs(
        status=None if status_filter == "All" else status_filter
    )
    
    if not jobs:
        st.info("No jobs found. Create one using the chat!")
    else:
        for job in jobs:
            with st.expander(f"**{job['title']}** - {job['company_name']} ({job['status']})"):
                st.markdown(f"**Location:** {job['location']}")
                st.markdown(f"**Type:** {job['employment_type']}")
                st.markdown(f"**Created:** {job['created_at']}")
                st.markdown("---")
                st.markdown(job['description'][:500] + "...")
                
                if st.button(f"View Details", key=f"job_{job['id']}"):
                    st.session_state.selected_job = job['id']


def render_candidates_page():
    """Render candidates listing"""
    st.markdown('<div class="main-header">👥 Candidates</div>', unsafe_allow_html=True)
    
    # Filter
    col1, col2 = st.columns([3, 1])
    with col1:
        status_filter = st.selectbox(
            "Filter by status",
            ["All", "new", "screening", "interview", "offer", "hired", "rejected"]
        )
    
    # Get candidates
    candidates = db_service.list_candidates(
        status=None if status_filter == "All" else status_filter
    )
    
    if not candidates:
        st.info("No candidates found. Upload resumes using the chat!")
    else:
        # Create table
        table_data = []
        for candidate in candidates:
            table_data.append({
                "Name": candidate['name'],
                "Email": candidate['email'],
                "Status": candidate['status'],
                "Match Score": f"{candidate.get('match_score', 0)}%",
                "Applied": candidate['created_at'][:10]
            })
        
        st.dataframe(table_data, use_container_width=True)


def render_interviews_page():
    """Render interviews calendar"""
    st.markdown('<div class="main-header">📅 Interviews</div>', unsafe_allow_html=True)
    
    from agents.interview_agent import interview_agent
    
    # Get upcoming interviews
    upcoming = interview_agent.list_upcoming_interviews(days_ahead=30)
    
    if not upcoming:
        st.info("No upcoming interviews scheduled")
    else:
        st.subheader(f"Upcoming Interviews ({len(upcoming)})")
        
        for interview in upcoming:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**{interview['candidate_name']}**")
                st.caption(interview['position'])
            
            with col2:
                st.markdown(f"📅 {interview['scheduled_date']}")
                st.caption(f"⏰ {interview['scheduled_time']}")
            
            with col3:
                st.markdown(f"**{interview['status']}**")


def main():
    """Main application"""
    initialize_session()
    
    if not st.session_state.initialized:
        st.error("⚠️ Please configure GEMINI_API_KEY in .env file")
        st.stop()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "💬 Chat":
        render_chat_page()
    elif page == "📊 Dashboard":
        render_dashboard()
    elif page == "📋 Jobs":
        render_jobs_page()
    elif page == "👥 Candidates":
        render_candidates_page()
    elif page == "📅 Interviews":
        render_interviews_page()


if __name__ == "__main__":
    main()
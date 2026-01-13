"""
Reusable UI components for Streamlit interface
"""
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime


def render_metric_card(
    title: str,
    value: Any,
    delta: Optional[str] = None,
    icon: str = "📊"
):
    """Render a metric card"""
    with st.container():
        st.markdown(f"### {icon} {title}")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric(label="", value=value, delta=delta)


def render_status_badge(status: str) -> str:
    """Render status badge with color"""
    
    status_colors = {
        'new': '🔵',
        'screening': '🟡',
        'interview': '🟠',
        'offer': '🟢',
        'hired': '✅',
        'rejected': '❌',
        'draft': '📝',
        'active': '🟢',
        'paused': '⏸️',
        'closed': '🔒'
    }
    
    emoji = status_colors.get(status.lower(), '⚪')
    return f"{emoji} {status.title()}"


def render_candidate_card(candidate: Dict[str, Any]):
    """Render candidate information card"""
    
    with st.expander(f"👤 {candidate['name']} - {render_status_badge(candidate['status'])}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Email:** {candidate['email']}")
            if candidate.get('phone'):
                st.markdown(f"**Phone:** {candidate['phone']}")
            st.markdown(f"**Applied:** {candidate['created_at'][:10]}")
        
        with col2:
            if candidate.get('match_score'):
                st.progress(candidate['match_score'] / 100)
                st.caption(f"Match Score: {candidate['match_score']}%")
            
            st.markdown(f"**Status:** {candidate['status']}")


def render_job_card(job: Dict[str, Any]):
    """Render job posting card"""
    
    with st.container():
        st.markdown(f"### 📋 {job['title']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Company:** {job['company_name']}")
            st.markdown(f"**Location:** {job['location']}")
        
        with col2:
            st.markdown(f"**Type:** {job['employment_type']}")
            st.markdown(f"**Status:** {render_status_badge(job['status'])}")
        
        with col3:
            st.markdown(f"**Created:** {job['created_at'][:10]}")
            if job.get('updated_at'):
                st.markdown(f"**Updated:** {job['updated_at'][:10]}")
        
        with st.expander("View Description"):
            st.markdown(job.get('description', 'No description available'))


def render_interview_card(interview: Dict[str, Any]):
    """Render interview schedule card"""
    
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**👤 Candidate**")
            st.markdown(interview.get('candidate_name', 'Unknown'))
            st.caption(interview.get('position', 'Unknown Position'))
        
        with col2:
            st.markdown(f"**📅 Schedule**")
            st.markdown(interview.get('scheduled_date', 'TBD'))
            st.caption(interview.get('scheduled_time', 'TBD'))
        
        with col3:
            st.markdown(f"**Status**")
            st.markdown(render_status_badge(interview.get('status', 'scheduled')))


def render_analytics_chart(
    data: Dict[str, int],
    title: str,
    chart_type: str = "bar"
):
    """Render analytics chart"""
    
    st.subheader(title)
    
    if chart_type == "bar":
        st.bar_chart(data)
    elif chart_type == "line":
        st.line_chart(data)
    elif chart_type == "area":
        st.area_chart(data)


def render_file_uploader(
    label: str = "Upload Resume",
    accepted_types: List[str] = ["pdf", "docx", "txt"]
) -> Optional[Any]:
    """Render file uploader component"""
    
    uploaded_file = st.file_uploader(
        label,
        type=accepted_types,
        help=f"Accepted formats: {', '.join(accepted_types)}"
    )
    
    return uploaded_file


def render_confirmation_dialog(
    message: str,
    confirm_label: str = "Confirm",
    cancel_label: str = "Cancel"
) -> bool:
    """Render confirmation dialog"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        confirm = st.button(confirm_label, type="primary")
    
    with col2:
        cancel = st.button(cancel_label)
    
    return confirm


def render_timeline(events: List[Dict[str, Any]]):
    """Render timeline of events"""
    
    st.markdown("### 📅 Timeline")
    
    for event in events:
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                st.markdown(f"**{event.get('date', 'N/A')}**")
            
            with col2:
                st.markdown(f"**{event.get('title', 'Event')}**")
                if event.get('description'):
                    st.caption(event['description'])
            
            st.markdown("---")


def render_progress_bar(
    current: int,
    total: int,
    label: str = "Progress"
):
    """Render progress bar with label"""
    
    percentage = (current / total * 100) if total > 0 else 0
    
    st.markdown(f"**{label}**")
    st.progress(percentage / 100)
    st.caption(f"{current} of {total} ({percentage:.1f}%)")


def render_table(
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None
):
    """Render data table"""
    
    if not data:
        st.info("No data available")
        return
    
    if columns:
        # Filter to specified columns
        filtered_data = [
            {k: v for k, v in row.items() if k in columns}
            for row in data
        ]
        st.dataframe(filtered_data, use_container_width=True)
    else:
        st.dataframe(data, use_container_width=True)


def render_sidebar_filters(
    filter_options: Dict[str, List[str]]
) -> Dict[str, Any]:
    """Render sidebar filters"""
    
    st.sidebar.markdown("### 🔍 Filters")
    
    selected_filters = {}
    
    for filter_name, options in filter_options.items():
        selected = st.sidebar.selectbox(
            filter_name.replace('_', ' ').title(),
            ['All'] + options
        )
        
        if selected != 'All':
            selected_filters[filter_name] = selected
    
    return selected_filters


def render_action_buttons(
    actions: List[Dict[str, str]]
) -> Optional[str]:
    """Render action buttons"""
    
    cols = st.columns(len(actions))
    
    for idx, action in enumerate(actions):
        with cols[idx]:
            if st.button(
                action['label'],
                key=action.get('key', f"action_{idx}"),
                type=action.get('type', 'secondary')
            ):
                return action['value']
    
    return None


def render_search_bar(placeholder: str = "Search...") -> str:
    """Render search bar"""
    
    return st.text_input(
        "",
        placeholder=placeholder,
        key="search_input"
    )


def render_date_range_picker():
    """Render date range picker"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date")
    
    with col2:
        end_date = st.date_input("End Date")
    
    return start_date, end_date


def render_notification(
    message: str,
    type: str = "info"
):
    """Render notification"""
    
    if type == "success":
        st.success(message)
    elif type == "error":
        st.error(message)
    elif type == "warning":
        st.warning(message)
    else:
        st.info(message)


def render_empty_state(
    message: str,
    icon: str = "📭",
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """Render empty state"""
    
    st.markdown(f"<div style='text-align: center; padding: 3rem;'>", unsafe_allow_html=True)
    st.markdown(f"<h1>{icon}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 1.2rem; color: #666;'>{message}</p>", unsafe_allow_html=True)
    
    if action_label and action_callback:
        if st.button(action_label, key="empty_state_action"):
            action_callback()
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_loading_spinner(message: str = "Loading..."):
    """Render loading spinner"""
    
    with st.spinner(message):
        return st.empty()
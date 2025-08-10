"""
Simple CineMitr Dashboard for Local Development
Simplified version without complex dependencies
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simple configuration without environment dependencies
class SimpleConfig:
    def __init__(self):
        self.app_title = "CineMitr - Content Management Dashboard"
        self.app_icon = "📽️"
        self.brand_color = "#4F46E5"
        self.chart_height = 300
        
        # Color schemes
        self.status_colors = {
            "Ready": "#3B82F6",
            "Uploaded": "#10B981", 
            "In Progress": "#F59E0B",
            "New": "#EF4444"
        }
        
        self.priority_colors = {
            "High": "#EF4444",
            "Medium": "#F59E0B",
            "Low": "#10B981"
        }

# Simple data models
class DashboardData:
    @staticmethod
    def get_metrics():
        return {
            "total_movies": 127,
            "content_items": 2847,
            "uploaded": 1923,
            "uploaded_weekly_change": 47,
            "pending": 234,
            "upload_rate": 67.5
        }
    
    @staticmethod
    def get_status_distribution():
        return {
            "Ready": 45,
            "Uploaded": 38,
            "In Progress": 25,
            "New": 19
        }
    
    @staticmethod
    def get_priority_distribution():
        return {
            "High": 42,
            "Medium": 68,
            "Low": 17
        }
    
    @staticmethod
    def get_recent_activity():
        return [
            {
                "name": "12th Fail",
                "content_type": "Reel",
                "status": "Ready",
                "priority": "High",
                "updated": "2 hours ago"
            },
            {
                "name": "2 States",
                "content_type": "Trailer",
                "status": "Uploaded",
                "priority": "Medium",
                "updated": "4 hours ago"
            },
            {
                "name": "Laal Singh Chaddha",
                "content_type": "Movie",
                "status": "In Progress",
                "priority": "Medium",
                "updated": "6 hours ago"
            },
            {
                "name": "Unknown Content",
                "content_type": "Reel",
                "status": "New",
                "priority": "Low",
                "updated": "1 day ago"
            }
        ]

def render_css():
    """Render custom CSS styles"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4F46E5;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 0.5rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        .sidebar-brand {
            font-size: 1.5rem;
            font-weight: bold;
            color: #4F46E5;
            margin-bottom: 2rem;
        }
        
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .status-ready { background-color: #3B82F6; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; }
        .status-uploaded { background-color: #10B981; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; }
        .status-progress { background-color: #F59E0B; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; }
        .status-new { background-color: #EF4444; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.8rem; }
        
        .priority-high { border-left: 4px solid #EF4444; padding-left: 1rem; font-weight: 500; }
        .priority-medium { border-left: 4px solid #F59E0B; padding-left: 1rem; font-weight: 500; }
        .priority-low { border-left: 4px solid #10B981; padding-left: 1rem; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">📽️ CineMitr</div>', unsafe_allow_html=True)
        
        menu_items = [
            "📊 Dashboard",
            "🎬 Movies", 
            "📄 Content Items",
            "⬆️ Upload Pipeline",
            "📈 Analytics",
            "⚙️ Settings"
        ]
        
        selected_item = st.radio("", menu_items, index=0)
        
        st.markdown("---")
        st.subheader("Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.success("Data refreshed!")
            st.rerun()
        
        if st.button("📥 Import Data", use_container_width=True):
            st.success("Import functionality ready - connect your API!")
        
        if st.button("➕ Add Content", use_container_width=True):
            st.success("Add content functionality ready - connect your API!")
        
        st.info("💡 **Tip:** Connect your API endpoints to make buttons functional")
        
        return selected_item

def render_metrics_cards(config, metrics):
    """Render dashboard metrics cards"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    cards = [
        {
            "value": str(metrics["total_movies"]),
            "label": "Total Movies",
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        },
        {
            "value": f"{metrics['content_items']:,}",
            "label": "Content Items", 
            "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        },
        {
            "value": f"{metrics['uploaded']:,}",
            "label": f"Uploaded<br><small>+{metrics['uploaded_weekly_change']} this week</small>",
            "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        },
        {
            "value": str(metrics["pending"]),
            "label": "Pending",
            "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
        },
        {
            "value": f"{metrics['upload_rate']}%",
            "label": "Upload Rate",
            "gradient": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
        }
    ]
    
    columns = [col1, col2, col3, col4, col5]
    
    for col, card in zip(columns, cards):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="background: {card['gradient']};">
                <div class="metric-value">{card['value']}</div>
                <div class="metric-label">{card['label']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_status_chart(config, status_data):
    """Render status distribution chart"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("📊 Content Status Distribution")
    
    fig_pie = px.pie(
        values=list(status_data.values()),
        names=list(status_data.keys()),
        color_discrete_sequence=[config.status_colors[k] for k in status_data.keys()]
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=True, height=config.chart_height)
    
    st.plotly_chart(fig_pie, use_container_width=True)
    st.caption("🥧 Interactive Pie Chart - Shows status breakdown with hover details")
    st.markdown('</div>', unsafe_allow_html=True)

def render_priority_chart(config, priority_data):
    """Render priority distribution chart"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("⚡ Priority Distribution")
    
    fig_bar = px.bar(
        x=list(priority_data.keys()),
        y=list(priority_data.values()),
        color=list(priority_data.keys()),
        color_discrete_sequence=[config.priority_colors[k] for k in priority_data.keys()]
    )
    fig_bar.update_layout(showlegend=False, height=config.chart_height)
    fig_bar.update_traces(text=list(priority_data.values()), textposition='outside')
    
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption("📊 Interactive Bar Chart - Color-coded priority levels")
    st.markdown('</div>', unsafe_allow_html=True)

def render_recent_activity(activity_data):
    """Render recent activity table"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("🕐 Recent Activity")
    
    # Table header
    header_cols = st.columns([3, 2, 2, 2, 2])
    headers = ["Movie Name", "Content Type", "Status", "Priority", "Updated"]
    
    for col, header in zip(header_cols, headers):
        with col:
            st.markdown(f"**{header}**")
    
    # Table rows
    for item in activity_data:
        cols = st.columns([3, 2, 2, 2, 2])
        
        with cols[0]:
            priority_class = f"priority-{item['priority'].lower()}"
            st.markdown(f'<div class="{priority_class}">{item["name"]}</div>', 
                       unsafe_allow_html=True)
        
        with cols[1]:
            st.write(item['content_type'])
        
        with cols[2]:
            status_class = f"status-{item['status'].lower().replace(' ', '-')}"
            st.markdown(f'<span class="{status_class}">{item["status"]}</span>', 
                       unsafe_allow_html=True)
        
        with cols[3]:
            st.write(item['priority'])
        
        with cols[4]:
            st.write(item['updated'])
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_other_pages(page_name):
    """Render other pages"""
    st.header(f"{page_name}")
    st.info(f"{page_name} functionality - Ready for API integration!")
    
    if "Movies" in page_name:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Add New Movie", use_container_width=True):
                st.success("Add movie API ready!")
        with col2:
            if st.button("Import Movies", use_container_width=True):
                st.success("Import API ready!")
        with col3:
            if st.button("Export Movies", use_container_width=True):
                st.success("Export API ready!")
    
    elif "Upload" in page_name:
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            st.success(f"File '{uploaded_file.name}' ready for processing!")
    
    elif "Analytics" in page_name:
        if st.button("Generate Report"):
            st.success("Report generation API ready!")
    
    elif "Settings" in page_name:
        st.subheader("Configuration")
        st.write("API Base URL:", "Ready for configuration")
        st.write("Environment:", "Development")
        if st.button("Save Settings"):
            st.success("Settings save API ready!")

def main():
    """Main application function"""
    # Configure Streamlit
    st.set_page_config(
        page_title="CineMitr - Content Management Dashboard",
        page_icon="📽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize simple configuration and data
    config = SimpleConfig()
    data = DashboardData()
    
    # Render CSS
    render_css()
    
    # Render sidebar and get selection
    selected_page = render_sidebar()
    
    # Route to appropriate page
    if "Dashboard" in selected_page:
        # Main dashboard
        st.markdown('<h1 class="main-header">📽️ Content Management Dashboard</h1>', 
                   unsafe_allow_html=True)
        
        # Get data
        metrics = data.get_metrics()
        status_dist = data.get_status_distribution()
        priority_dist = data.get_priority_distribution()
        recent_activity = data.get_recent_activity()
        
        # Render components
        render_metrics_cards(config, metrics)
        
        # Charts
        col_left, col_right = st.columns(2)
        with col_left:
            render_status_chart(config, status_dist)
        with col_right:
            render_priority_chart(config, priority_dist)
        
        # Recent activity
        render_recent_activity(recent_activity)
        
        # Footer
        current_time = datetime.now().strftime("%I:%M %p | %d-%m-%Y")
        st.markdown(f"""
        ---
        <div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
            <strong>{current_time}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Other pages
        render_other_pages(selected_page)

if __name__ == "__main__":
    # Check if running directly with python
    import sys
    if len(sys.argv) == 1:  # No streamlit arguments
        print("Starting CineMitr Dashboard...")
        print("If this doesn't work, try: python -m streamlit run cinemitr_dashboard_simple.py")
        print("Dashboard will be available at: http://localhost:8501")
        print("-" * 60)
        
        # Try to run with streamlit
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "-m", "streamlit", "run", __file__,
                "--server.headless=false"
            ], check=True)
        except Exception as e:
            print(f"Could not start with streamlit: {e}")
            print("Please run manually: python -m streamlit run cinemitr_dashboard_simple.py")
    else:
        main()
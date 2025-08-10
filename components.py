import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
from config import DashboardConfig, MENU_ITEMS, QUICK_ACTIONS
from api_service import APIService, DashboardMetrics, StatusDistribution, PriorityDistribution, ContentItem

class UIComponents:
    def __init__(self, config: DashboardConfig, api_service: APIService):
        self.config = config
        self.api_service = api_service
    
    def render_custom_css(self):
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
                display: flex;
                align-items: center;
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
    
    def render_sidebar(self) -> str:
        """Render sidebar navigation and return selected item"""
        with st.sidebar:
            st.markdown('<div class="sidebar-brand">📽️ CineMitr</div>', unsafe_allow_html=True)
            
            # Navigation Menu
            menu_options = [f"{item['icon']} {item['label']}" for item in MENU_ITEMS]
            selected_item = st.radio("", menu_options, index=0)
            
            # Get the selected key
            selected_key = None
            for i, item in enumerate(MENU_ITEMS):
                if selected_item == f"{item['icon']} {item['label']}":
                    selected_key = item['key']
                    break
            
            st.markdown("---")
            st.subheader("Quick Actions")
            
            # Quick Action Buttons
            for action in QUICK_ACTIONS:
                if st.button(f"{action['icon']} {action['label']}", 
                           key=action['action'], 
                           use_container_width=True):
                    self._handle_quick_action(action['action'])
            
            st.info("💡 **Tip:** Use filters to quickly find content")
            
            return selected_key
    
    def _handle_quick_action(self, action: str):
        """Handle quick action button clicks"""
        if action == "refresh_data":
            if self.api_service.refresh_data():
                st.success("Data refreshed successfully!")
                st.rerun()
            else:
                st.error("Failed to refresh data")
        
        elif action == "import_data":
            st.info("Import data functionality - API integration ready")
            # You can add file upload widget here when API is ready
        
        elif action == "add_content":
            st.success("Add content dialog - API integration ready")
            # You can add form modal here when API is ready
    
    def render_header(self):
        """Render main dashboard header"""
        st.markdown('<h1 class="main-header">📽️ Content Management Dashboard</h1>', 
                   unsafe_allow_html=True)
    
    def render_metrics_cards(self, metrics: DashboardMetrics):
        """Render dashboard metrics cards"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metric_configs = [
            {
                "value": str(metrics.total_movies),
                "label": "Total Movies",
                "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            },
            {
                "value": f"{metrics.content_items:,}",
                "label": "Content Items", 
                "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            },
            {
                "value": f"{metrics.uploaded:,}",
                "label": f"Uploaded<br><small>+{metrics.uploaded_weekly_change} this week</small>",
                "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            },
            {
                "value": str(metrics.pending),
                "label": "Pending",
                "gradient": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
            },
            {
                "value": f"{metrics.upload_rate}%",
                "label": "Upload Rate",
                "gradient": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"
            }
        ]
        
        columns = [col1, col2, col3, col4, col5]
        
        for i, (col, config) in enumerate(zip(columns, metric_configs)):
            with col:
                st.markdown(f"""
                <div class="metric-card" style="background: {config['gradient']};">
                    <div class="metric-value">{config['value']}</div>
                    <div class="metric-label">{config['label']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_status_chart(self, status_dist: StatusDistribution):
        """Render content status distribution chart"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Content Status Distribution")
        
        status_data = {
            'Status': ['Ready', 'Uploaded', 'In Progress', 'New'],
            'Count': [status_dist.ready, status_dist.uploaded, 
                     status_dist.in_progress, status_dist.new],
            'Color': [self.config.status_colors['Ready'],
                     self.config.status_colors['Uploaded'],
                     self.config.status_colors['In Progress'],
                     self.config.status_colors['New']]
        }
        
        fig_pie = px.pie(
            values=status_data['Count'],
            names=status_data['Status'],
            color_discrete_sequence=status_data['Color']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=True, height=self.config.chart_height)
        
        st.plotly_chart(fig_pie, use_container_width=True)
        st.caption("🥧 Interactive Pie Chart - Shows status breakdown with hover details")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_priority_chart(self, priority_dist: PriorityDistribution):
        """Render priority distribution chart"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("⚡ Priority Distribution")
        
        priority_data = {
            'Priority': ['High', 'Medium', 'Low'],
            'Count': [priority_dist.high, priority_dist.medium, priority_dist.low],
            'Color': [self.config.priority_colors['High'],
                     self.config.priority_colors['Medium'],
                     self.config.priority_colors['Low']]
        }
        
        fig_bar = px.bar(
            x=priority_data['Priority'],
            y=priority_data['Count'],
            color=priority_data['Priority'],
            color_discrete_sequence=priority_data['Color']
        )
        fig_bar.update_layout(showlegend=False, height=self.config.chart_height)
        fig_bar.update_traces(text=priority_data['Count'], textposition='outside')
        
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("📊 Interactive Bar Chart - Color-coded priority levels")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_recent_activity(self, activity_data: List[ContentItem]):
        """Render recent activity table"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🕐 Recent Activity")
        
        # Table header
        header_cols = st.columns([3, 2, 2, 2, 2, 1])
        headers = ["Movie Name", "Content Type", "Status", "Priority", "Updated", "Action"]
        
        for col, header in zip(header_cols, headers):
            with col:
                st.markdown(f"**{header}**")
        
        # Table rows
        for item in activity_data:
            cols = st.columns([3, 2, 2, 2, 2, 1])
            
            with cols[0]:
                priority_class = f"priority-{item.priority.value.lower()}"
                st.markdown(f'<div class="{priority_class}">{item.name}</div>', 
                           unsafe_allow_html=True)
            
            with cols[1]:
                st.write(item.content_type.value)
            
            with cols[2]:
                status_class = f"status-{item.status.value.lower().replace(' ', '-')}"
                st.markdown(f'<span class="{status_class}">{item.status.value}</span>', 
                           unsafe_allow_html=True)
            
            with cols[3]:
                st.write(item.priority.value)
            
            with cols[4]:
                st.write(item.updated)
            
            with cols[5]:
                if st.button("⋮", key=f"action_{item.id}", help="More actions"):
                    self._handle_content_action(item)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _handle_content_action(self, item: ContentItem):
        """Handle content action menu"""
        st.info(f"Action menu for {item.name} - API integration ready")
        # You can implement action menu (edit, delete, etc.) here
    
    def render_footer(self):
        """Render dashboard footer"""
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%d-%m-%Y")
        
        st.markdown(f"""
        ---
        <div style="text-align: center; color: #666; font-size: 0.9rem; margin-top: 2rem;">
            <strong>{current_time} | {current_date}</strong>
        </div>
        """, unsafe_allow_html=True)
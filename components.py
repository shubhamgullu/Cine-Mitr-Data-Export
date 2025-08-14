import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
from config import DashboardConfig, MENU_ITEMS, QUICK_ACTIONS
from api_service import APIService, DashboardMetrics, StatusDistribution, PriorityDistribution, ContentItem

class UIComponents:
    def __init__(self, config: DashboardConfig, api_service: APIService):
        self.config = config
        self.api_service = api_service
    
    def render_custom_css(self):
        """Render enhanced CSS styles matching the updated UI"""
        st.markdown("""
        <style>
            /* Header and branding */
            .main-header {
                font-size: 2rem;
                font-weight: bold;
                color: #5B21B6;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .api-types-badge {
                background: linear-gradient(45deg, #5B21B6, #7C3AED);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-size: 0.8rem;
                margin-left: 1rem;
            }
            
            /* Enhanced metric cards */
            .metric-card {
                background: white;
                border: 1px solid #E5E7EB;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                margin: 0.5rem 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
                color: #1F2937;
            }
            
            .metric-label {
                font-size: 0.9rem;
                color: #6B7280;
                font-weight: 500;
            }
            
            .metric-change {
                font-size: 0.8rem;
                color: #10B981;
                margin-top: 0.25rem;
            }
            
            /* Sidebar styling */
            .sidebar-brand {
                font-size: 1.5rem;
                font-weight: bold;
                color: #5B21B6;
                margin-bottom: 2rem;
                display: flex;
                align-items: center;
            }
            
            /* Filter section */
            .filter-section {
                background: #F9FAFB;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border: 1px solid #E5E7EB;
            }
            
            /* Action buttons */
            .action-button {
                background: white;
                border: 1px solid #D1D5DB;
                padding: 0.5rem 1rem;
                border-radius: 6px;
                margin: 0.25rem;
                cursor: pointer;
                display: inline-block;
                font-size: 0.9rem;
                transition: all 0.2s ease;
            }
            
            .action-button:hover {
                background: #F3F4F6;
                border-color: #9CA3AF;
            }
            
            .action-button.primary {
                background: #3B82F6;
                color: white;
                border-color: #3B82F6;
            }
            
            .action-button.success {
                background: #10B981;
                color: white;
                border-color: #10B981;
            }
            
            .action-button.warning {
                background: #F59E0B;
                color: white;
                border-color: #F59E0B;
            }
            
            /* Chart containers */
            .chart-container {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin: 1rem 0;
                border: 1px solid #E5E7EB;
            }
            
            .chart-title {
                font-size: 1.1rem;
                font-weight: 600;
                color: #1F2937;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
            }
            
            /* Status badges */
            .status-ready { 
                background-color: #3B82F6; 
                color: white; 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem;
                font-weight: 500;
            }
            .status-uploaded { 
                background-color: #10B981; 
                color: white; 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem;
                font-weight: 500;
            }
            .status-in-progress { 
                background-color: #F59E0B; 
                color: white; 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem;
                font-weight: 500;
            }
            .status-new { 
                background-color: #EF4444; 
                color: white; 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem;
                font-weight: 500;
            }
            
            /* Priority indicators */
            .priority-high { 
                border-left: 4px solid #EF4444; 
                padding-left: 1rem; 
                font-weight: 500; 
            }
            .priority-medium { 
                border-left: 4px solid #F59E0B; 
                padding-left: 1rem; 
                font-weight: 500; 
            }
            .priority-low { 
                border-left: 4px solid #10B981; 
                padding-left: 1rem; 
                font-weight: 500; 
            }
            
            /* Storage section */
            .storage-info {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            
            .storage-bar {
                background: rgba(255,255,255,0.3);
                border-radius: 4px;
                height: 8px;
                margin: 0.5rem 0;
                overflow: hidden;
            }
            
            .storage-fill {
                background: white;
                height: 100%;
                border-radius: 4px;
                transition: width 0.3s ease;
            }
            
            /* File upload area */
            .upload-area {
                border: 2px dashed #D1D5DB;
                border-radius: 8px;
                padding: 2rem;
                text-align: center;
                background: #F9FAFB;
                margin: 1rem 0;
                transition: all 0.2s ease;
            }
            
            .upload-area:hover {
                border-color: #3B82F6;
                background: #EFF6FF;
            }
            
            /* API endpoint tags */
            .api-endpoint {
                background: #F3F4F6;
                color: #374151;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-family: monospace;
                font-size: 0.75rem;
                margin: 0.25rem;
                display: inline-block;
            }
            
            .api-get { background: #DBEAFE; color: #1E40AF; }
            .api-post { background: #D1FAE5; color: #065F46; }
            .api-put { background: #FEF3C7; color: #92400E; }
            .api-delete { background: #FEE2E2; color: #991B1B; }
        </style>
        """, unsafe_allow_html=True)
    
    def render_header_with_api_info(self):
        """Render enhanced header with API endpoint information"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            <div class="main-header">
                📽️ Content Management Dashboard
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="api-types-badge">
                <div style="font-weight: bold;">API Types</div>
                <div style="font-size: 0.7rem; margin-top: 0.25rem;">
                    🟢 Core APIs<br>
                    🟡 Enhanced APIs<br>
                    🔵 New APIs
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    def render_api_endpoints_sidebar(self):
        """Render API endpoints in sidebar"""
        with st.sidebar:
            st.markdown("### 🔗 API Endpoints")
            
            # Group endpoints by category
            api_groups = {
                "Dashboard": [
                    ("GET", "/api/movies", "🟢"),
                    ("GET", "/api/content-items", "🟡"),
                    ("GET", "/api/upload/actions", "🔵"),
                ],
                "Analytics": [
                    ("GET", "/api/analytics/*", "🔵"),
                    ("GET", "/api/dashboard/recent-activity", "🟡"),
                ],
                "Management": [
                    ("POST", "/api/bulk-operations", "🔵"),
                    ("GET", "/api/storage/stats", "🔵"),
                ]
            }
            
            for group, endpoints in api_groups.items():
                st.markdown(f"**{group}**")
                for method, endpoint, status in endpoints:
                    color_class = "api-get" if method == "GET" else "api-post"
                    st.markdown(f"""
                    <div style="margin: 0.25rem 0;">
                        {status} <span class="{color_class}">{method}</span> 
                        <span style="font-size: 0.8rem;">{endpoint}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("")
    
    def render_sidebar(self) -> str:
        """Render enhanced sidebar navigation"""
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
            
            # Storage Usage Section
            self.render_storage_sidebar()
            
            st.markdown("---")
            self.render_api_endpoints_sidebar()
            
            return selected_key
    
    def render_storage_sidebar(self):
        """Render storage usage in sidebar"""
        st.markdown("### 💾 Storage Usage")
        
        # Mock storage data - replace with API call
        used_gb = 680
        total_gb = 1000
        usage_percent = (used_gb / total_gb) * 100
        
        st.markdown(f"""
        <div class="storage-info">
            <div style="font-size: 1.2rem; font-weight: bold;">{used_gb} GB used</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">{total_gb} GB total</div>
            <div class="storage-bar">
                <div class="storage-fill" style="width: {usage_percent}%;"></div>
            </div>
            <div style="font-size: 0.8rem; margin-top: 0.5rem;">{usage_percent:.1f}% used</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_enhanced_metrics(self, metrics: DashboardMetrics):
        """Render enhanced metrics cards with trends"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        metric_configs = [
            {
                "value": "127",
                "label": "Total Movies",
                "change": "+4 this month",
                "color": "#3B82F6"
            },
            {
                "value": "2,847",
                "label": "Content Items", 
                "change": "+124 this week",
                "color": "#10B981"
            },
            {
                "value": "1,923",
                "label": "Uploaded",
                "change": "+17 today",
                "color": "#8B5CF6"
            },
            {
                "value": "234",
                "label": "Pending",
                "change": "-12 vs yesterday",
                "color": "#F59E0B"
            },
            {
                "value": "67.5%",
                "label": "Upload Rate",
                "change": "+2.3% vs last week",
                "color": "#EF4444"
            }
        ]
        
        columns = [col1, col2, col3, col4, col5]
        
        for col, config in zip(columns, metric_configs):
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {config['color']};">{config['value']}</div>
                    <div class="metric-label">{config['label']}</div>
                    <div class="metric-change">{config['change']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def render_filters_and_actions(self):
        """Render filters and action buttons"""
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        # Filters row
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        
        with col1:
            status_filter = st.selectbox("All Status", 
                                       ["All Status", "Ready", "Uploaded", "In Progress", "New"],
                                       key="status_filter")
        
        with col2:
            type_filter = st.selectbox("All Types", 
                                     ["All Types", "Movie", "Reel", "Trailer"],
                                     key="type_filter")
        
        with col3:
            priority_filter = st.selectbox("All Priority", 
                                         ["All Priority", "High", "Medium", "Low"],
                                         key="priority_filter")
        
        with col4:
            view_mode = st.selectbox("View", 
                                   ["📊 Table", "🔲 Grid"],
                                   key="view_mode")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons row
        st.markdown("### Quick Actions")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        action_buttons = [
            ("📤 Export Data", "primary", "export_data"),
            ("📁 Bulk Upload", "success", "bulk_upload"), 
            ("🧹 Cleanup", "warning", "cleanup"),
            ("🔄 Refresh", "action", "refresh"),
            ("📊 Analytics", "primary", "analytics")
        ]
        
        columns = [col1, col2, col3, col4, col5]
        for col, (label, btn_type, key) in zip(columns, action_buttons):
            with col:
                if st.button(label, key=key, use_container_width=True):
                    self._handle_action_button(key)
    
    def _handle_action_button(self, action: str):
        """Handle action button clicks"""
        if action == "export_data":
            st.success("🚀 Export started! Check downloads folder.")
        elif action == "bulk_upload":
            st.info("📁 Bulk upload modal opened")
        elif action == "cleanup":
            st.warning("🧹 Cleanup process initiated")
        elif action == "refresh":
            st.success("🔄 Data refreshed successfully!")
            st.rerun()
        elif action == "analytics":
            st.info("📊 Analytics dashboard loading...")
    
    def render_file_upload_area(self):
        """Render drag & drop file upload area"""
        st.markdown("""
        <div class="upload-area">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
            <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">
                Drag & drop files here or click to browse
            </div>
            <div style="color: #6B7280; font-size: 0.9rem;">
                Supports MP4, MOV, JPG, PNG up to 2GB each • Multiple files supported
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['mp4', 'mov', 'jpg', 'jpeg', 'png'],
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) ready for upload")
            for file in uploaded_files:
                st.write(f"📄 {file.name} ({file.size / 1024 / 1024:.1f} MB)")
    
    def render_interactive_status_chart(self, status_dist: StatusDistribution):
        """Render interactive status distribution pie chart"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Content Status Distribution</div>', unsafe_allow_html=True)
        
        # Data for pie chart
        labels = ['Ready', 'Uploaded', 'In Progress', 'New'] 
        values = [status_dist.ready, status_dist.uploaded, status_dist.in_progress, status_dist.new]
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
        
        # Create interactive pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Count: %{value}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🎯 Interactive Pie Chart - Click legend to filter, hover for details")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_priority_bar_chart(self, priority_dist: PriorityDistribution):
        """Render priority distribution bar chart"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">⚡ Priority Distribution</div>', unsafe_allow_html=True)
        
        # Data for bar chart
        priorities = ['High', 'Medium', 'Low']
        values = [priority_dist.high, priority_dist.medium, priority_dist.low]
        colors = ['#EF4444', '#F59E0B', '#10B981']
        
        # Create interactive bar chart
        fig = go.Figure(data=[go.Bar(
            x=priorities,
            y=values,
            marker_color=colors,
            text=values,
            textposition='outside',
            hovertemplate='<b>%{x} Priority</b><br>' +
                         'Count: %{y}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=False,
            height=300,
            margin=dict(t=20, b=40, l=20, r=20),
            xaxis_title="Priority Level",
            yaxis_title="Number of Items",
            font=dict(size=12)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("📊 Priority Bar Chart - Hover for item counts")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_storage_donut_chart(self):
        """Render storage usage donut chart"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">💾 Storage by Type</div>', unsafe_allow_html=True)
        
        # Mock storage data by type
        storage_data = {
            'Type': ['Movies', 'Reels', 'Trailers', 'Other'],
            'Size_GB': [450, 150, 60, 20],
            'Colors': ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B']
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=storage_data['Type'],
            values=storage_data['Size_GB'],
            hole=0.5,
            marker_colors=storage_data['Colors'],
            textinfo='label+value',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Size: %{value} GB<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=True,
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            annotations=[dict(text='Storage<br>Donut Chart', x=0.5, y=0.5, font_size=12, showarrow=False)]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption("💽 Storage Donut Chart - Content type breakdown")
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_enhanced_recent_activity(self, activity_data: List[ContentItem]):
        """Render enhanced recent activity with selection and actions"""
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🕐 Recent Activity</div>', unsafe_allow_html=True)
        
        # Activity controls
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("3 items selected", key="selection_info"):
                st.info("Selection actions: Delete, Change Status, Export")
        with col2:
            st.button("Delete", key="delete_selected")
        with col3:
            st.button("Change Status", key="change_status")
            st.button("Export", key="export_selected")
        
        # Enhanced activity table
        for i, item in enumerate(activity_data[:10]):  # Show first 10 items
            with st.container():
                cols = st.columns([0.5, 3, 1.5, 1.5, 1.5, 1.5, 0.5])
                
                with cols[0]:
                    st.checkbox("", key=f"select_{item.id}", value=(i < 3))  # First 3 selected
                
                with cols[1]:
                    priority_class = f"priority-{item.priority.value.lower()}"
                    st.markdown(f'<div class="{priority_class}">{item.name}</div>', 
                               unsafe_allow_html=True)
                
                with cols[2]:
                    st.write(item.content_type.value)
                
                with cols[3]:
                    status_class = f"status-{item.status.value.lower().replace(' ', '-')}"
                    st.markdown(f'<span class="{status_class}">{item.status.value}</span>', 
                               unsafe_allow_html=True)
                
                with cols[4]:
                    st.write(item.priority.value)
                
                with cols[5]:
                    st.write(item.updated)
                
                with cols[6]:
                    if st.button("⋮", key=f"action_{item.id}", help="More actions"):
                        self._show_item_actions(item)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _show_item_actions(self, item: ContentItem):
        """Show item action menu"""
        with st.popover(f"Actions for {item.name}"):
            if st.button("📝 Edit", key=f"edit_{item.id}"):
                st.success(f"Editing {item.name}")
            if st.button("🗑️ Delete", key=f"delete_{item.id}"):
                st.error(f"Deleting {item.name}")
            if st.button("📊 View Analytics", key=f"analytics_{item.id}"):
                st.info(f"Analytics for {item.name}")
    
    def render_footer(self):
        """Render enhanced footer"""
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%d-%m-%Y")
        
        st.markdown(f"""
        ---
        <div style="text-align: center; color: #6B7280; font-size: 0.9rem; margin-top: 2rem;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 2rem;">
                <div><strong>🕐 {current_time} | 📅 {current_date}</strong></div>
                <div>🔗 API Status: <span style="color: #10B981;">●</span> Connected</div>
                <div>📊 Real-time Updates: <span style="color: #10B981;">●</span> Active</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
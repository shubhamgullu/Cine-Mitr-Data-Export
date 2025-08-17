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
    
    def render_add_movie_form(self):
        """Render add movie form with API integration"""
        with st.form("add_movie_form", clear_on_submit=True):
            st.markdown("### 🎬 Add New Movie")
            st.info("💡 **Tip:** Fill in the required fields (*) and any additional details, then click **Add Movie** to create.")
            
            # Basic Information
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Movie Title *", placeholder="Enter movie title")
                genre = st.selectbox("Genre *", [
                    "Action", "Adventure", "Comedy", "Drama", "Horror", 
                    "Romance", "Sci-Fi", "Thriller", "Documentary", "Animation"
                ])
                director = st.text_input("Director", placeholder="Director name")
                language = st.selectbox("Language", [
                    "Hindi", "English", "Tamil", "Telugu", "Malayalam", 
                    "Bengali", "Marathi", "Gujarati", "Punjabi", "Other"
                ])
            
            with col2:
                release_date = st.date_input("Release Date")
                duration_minutes = st.number_input("Duration (minutes)", min_value=1, max_value=1000, value=120)
                rating = st.selectbox("Rating", ["U", "U/A", "A", "S", "Not Rated"])
                country = st.text_input("Country", value="India")
                
                # Status selection for new movie
                status = st.selectbox("Status", ["New", "Ready", "In Progress", "Uploaded", "Processing", "Failed"], index=0)
            
            # Additional Information
            st.markdown("#### Additional Details")
            description = st.text_area("Description", placeholder="Brief description of the movie", max_chars=2000)
            
            # Cast (multi-line input)
            cast_input = st.text_area("Cast (one name per line)", placeholder="Actor 1\nActor 2\nActor 3...")
            
            # File upload for poster
            poster_file = st.file_uploader("Movie Poster", type=['jpg', 'jpeg', 'png'], help="Upload movie poster image")
            
            # Submit button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submit_button = st.form_submit_button("🎬 Add Movie", use_container_width=True, type="primary")
            
            if submit_button:
                # Validate required fields
                if not title or not genre:
                    st.error("❌ Please fill in all required fields (marked with *)")
                    return False
                
                # Process cast list
                cast_list = []
                if cast_input:
                    cast_list = [name.strip() for name in cast_input.split('\n') if name.strip()]
                
                # Prepare movie data
                movie_data = {
                    "title": title,
                    "genre": genre,
                    "release_date": release_date.isoformat() if release_date else None,
                    "duration_minutes": duration_minutes,
                    "description": description if description else None,
                    "director": director if director else None,
                    "cast": cast_list if cast_list else None,
                    "rating": rating if rating != "Not Rated" else None,
                    "language": language,
                    "country": country,
                    "status": status
                }
                
                # Call API to create movie
                success = self._create_movie_via_api(movie_data)
                
                if success:
                    st.success(f"🎉 **{title}** added successfully!")
                    st.balloons()
                    return True
                else:
                    st.error("❌ Failed to add movie. Please try again.")
                    return False
        
        return False
    
    def _create_movie_via_api(self, movie_data: dict) -> bool:
        """Create movie via API call"""
        try:
            import requests
            import json
            
            # API endpoint
            api_url = f"{self.config.api.base_url}/movies"
            headers = self.config.api.get_headers()
            
            # Make API call
            response = requests.post(
                api_url,
                json=movie_data,
                headers=headers,
                timeout=self.config.api.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Clear any cached data to refresh the movies list
                    if hasattr(self.api_service, 'refresh_data'):
                        self.api_service.refresh_data()
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return False
    
    def render_movies_list_with_checkbox(self, movies_list: List = None):
        """Render movies list with checkboxes for bulk operations"""
        st.markdown("### 🎬 Movies Management")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Export format selection
            export_format = st.selectbox("Export Format", ["csv", "json", "xlsx"], index=0, key="export_format")
            
            if st.button("📤 Export Selected", key="export_movies"):
                selected_movie_ids = [
                    k.replace("movie_select_", "") 
                    for k in st.session_state.keys() 
                    if k.startswith("movie_select_") and st.session_state[k]
                ]
                
                if len(selected_movie_ids) > 0:
                    # Start export process
                    with st.spinner(f"🚀 Exporting {len(selected_movie_ids)} movies to {export_format.upper()}..."):
                        result = self.api_service.export_movies(format=export_format, selected_ids=selected_movie_ids)
                        
                        if result["status"] == "success":
                            st.success(f"✅ {result['message']}")
                            
                            # Try to download the file after a short delay
                            import time
                            time.sleep(2)  # Wait for export to complete
                            
                            export_id = result.get("export_id")
                            if export_id:
                                file_content = self.api_service.download_export_file(export_id)
                                if file_content:
                                    # Provide download button
                                    st.download_button(
                                        label=f"⬇️ Download {export_format.upper()} File",
                                        data=file_content,
                                        file_name=f"movies_export.{export_format}",
                                        mime=self._get_mime_type(export_format),
                                        key="download_export"
                                    )
                                else:
                                    st.error("❌ Failed to download export file")
                        else:
                            st.error(f"❌ Export failed: {result['message']}")
                else:
                    st.warning("⚠️ Please select movies to export")
        
        with col2:
            if st.button("🗑️ Delete Selected", key="delete_movies"):
                selected_count = len([k for k in st.session_state.keys() if k.startswith("movie_select_") and st.session_state[k]])
                if selected_count > 0:
                    st.error(f"🗑️ Deleting {selected_count} selected movies...")
                else:
                    st.warning("⚠️ Please select movies to delete")
        
        with col3:
            if st.button("📊 Bulk Edit", key="bulk_edit_movies"):
                st.info("📝 Bulk edit functionality")
        
        with col4:
            if st.button("🔄 Refresh", key="refresh_movies"):
                # Clear any cached data and force refresh
                st.cache_data.clear()
                st.success("🔄 Movies list refreshed!")
                st.rerun()
        
        # Movies table with checkboxes
        if not movies_list:
            # Fetch movies from API service
            movies_list = self.api_service.get_movies_list()
        
        # Table header
        header_cols = st.columns([0.5, 3, 1.5, 1, 1.5, 1.5, 0.5])
        headers = ["☑️", "Movie Title", "Genre", "Duration", "Status", "Release Date", "Actions"]
        
        for col, header in zip(header_cols, headers):
            with col:
                st.markdown(f"**{header}**")
        
        # Table rows
        for movie in movies_list:
            cols = st.columns([0.5, 3, 1.5, 1, 1.5, 1.5, 0.5])
            
            with cols[0]:
                st.checkbox("", key=f"movie_select_{movie['id']}", label_visibility="collapsed")
            
            with cols[1]:
                st.markdown(f"**{movie['title']}**")
            
            with cols[2]:
                st.write(movie['genre'])
            
            with cols[3]:
                duration = movie.get('duration_minutes', movie.get('duration', 0))
                st.write(f"{duration} min")
            
            with cols[4]:
                status = movie['status']
                status_class = f"status-{status.lower().replace(' ', '-')}"
                st.markdown(f'<span class="{status_class}">{status}</span>', unsafe_allow_html=True)
            
            with cols[5]:
                release_date = movie.get('release_date')
                if release_date:
                    # Handle datetime strings - just take the date part
                    if 'T' in str(release_date):
                        release_date = release_date.split('T')[0]
                    st.write(release_date)
                else:
                    st.write("N/A")
            
            with cols[6]:
                if st.button("⋮", key=f"movie_action_{movie['id']}", help="Movie actions"):
                    self._handle_movie_actions(movie)
    
    def _handle_movie_actions(self, movie: Dict):
        """Handle movie action menu"""
        # Store selected movie in session state for editing
        st.session_state.selected_movie_for_edit = movie
        st.session_state.show_edit_movie_modal = True
        st.rerun()
    
    def _get_mime_type(self, format: str) -> str:
        """Get MIME type for export format"""
        mime_types = {
            "csv": "text/csv",
            "json": "application/json",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        return mime_types.get(format, "application/octet-stream")
    
    def render_edit_movie_form(self, movie_data: Dict):
        """Render edit movie form with pre-populated data"""
        with st.form("edit_movie_form", clear_on_submit=False):
            st.markdown(f"### ✏️ Edit Movie: {movie_data.get('title', 'Unknown')}")
            st.info("💡 **Tip:** All fields are pre-filled with current data. Make your changes and click **Update Movie** to save.")
            
            # Basic Information with pre-filled values
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Movie Title *", value=movie_data.get('title', ''), placeholder="Enter movie title")
                
                # Genre selection with current value
                genres = ["Action", "Adventure", "Comedy", "Drama", "Horror", 
                         "Romance", "Sci-Fi", "Thriller", "Documentary", "Animation"]
                current_genre = movie_data.get('genre', 'Drama')
                genre_index = genres.index(current_genre) if current_genre in genres else 0
                genre = st.selectbox("Genre *", genres, index=genre_index)
                
                director = st.text_input("Director", value=movie_data.get('director', ''), placeholder="Director name")
                
                # Language selection with current value
                languages = ["Hindi", "English", "Tamil", "Telugu", "Malayalam", 
                           "Bengali", "Marathi", "Gujarati", "Punjabi", "Other"]
                current_language = movie_data.get('language', 'Hindi')
                language_index = languages.index(current_language) if current_language in languages else 0
                language = st.selectbox("Language", languages, index=language_index)
            
            with col2:
                # Release date with current value
                from datetime import datetime, date
                current_release_date = movie_data.get('release_date', '')
                if current_release_date:
                    try:
                        if isinstance(current_release_date, str):
                            release_date_obj = datetime.fromisoformat(current_release_date.replace('Z', '+00:00')).date()
                        else:
                            release_date_obj = current_release_date
                    except:
                        release_date_obj = date.today()
                else:
                    release_date_obj = date.today()
                
                release_date = st.date_input("Release Date", value=release_date_obj)
                
                duration_minutes = st.number_input(
                    "Duration (minutes)", 
                    min_value=1, 
                    max_value=1000, 
                    value=movie_data.get('duration', 120)
                )
                
                # Rating selection with current value
                ratings = ["U", "U/A", "A", "S", "Not Rated"]
                current_rating = movie_data.get('rating', 'Not Rated')
                rating_index = ratings.index(current_rating) if current_rating in ratings else 4
                rating = st.selectbox("Rating", ratings, index=rating_index)
                
                country = st.text_input("Country", value=movie_data.get('country', 'India'))
                
                # Status selection with current value
                statuses = ["Ready", "Uploaded", "In Progress", "New", "Failed", "Processing"]
                current_status = movie_data.get('status', 'New')
                status_index = statuses.index(current_status) if current_status in statuses else 3
                status = st.selectbox("Status *", statuses, index=status_index)
            
            # Additional Information
            st.markdown("#### Additional Details")
            description = st.text_area(
                "Description", 
                value=movie_data.get('description', ''),
                placeholder="Brief description of the movie", 
                max_chars=2000
            )
            
            # Cast (convert list back to multi-line string)
            current_cast = movie_data.get('cast', [])
            cast_text = '\n'.join(current_cast) if isinstance(current_cast, list) else str(current_cast)
            cast_input = st.text_area("Cast (one name per line)", value=cast_text, placeholder="Actor 1\nActor 2\nActor 3...")
            
            # File upload for poster
            poster_file = st.file_uploader("Update Movie Poster", type=['jpg', 'jpeg', 'png'], help="Upload new movie poster image")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                update_button = st.form_submit_button("✏️ Update Movie", use_container_width=True, type="primary")
            
            with col2:
                cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            with col3:
                delete_button = st.form_submit_button("🗑️ Delete Movie", use_container_width=True)
            
            with col4:
                duplicate_button = st.form_submit_button("📋 Duplicate", use_container_width=True)
            
            # Handle form submissions
            if cancel_button:
                st.session_state.show_edit_movie_modal = False
                st.session_state.confirm_delete = False  # Reset delete confirmation
                st.info("✅ Edit cancelled. No changes were made.")
                st.rerun()
            
            if delete_button:
                if st.session_state.get('confirm_delete', False):
                    success = self._delete_movie_via_api(movie_data['id'])
                    if success:
                        st.success(f"🗑️ **{movie_data.get('title', 'Movie')}** deleted successfully!")
                        st.session_state.show_edit_movie_modal = False
                        st.session_state.confirm_delete = False  # Reset confirmation
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete movie.")
                else:
                    st.session_state.confirm_delete = True
                    st.warning(f"⚠️ Click Delete again to confirm deletion of **{movie_data.get('title', 'this movie')}**.")
                    st.rerun()
            
            if duplicate_button:
                # Create a copy with modified title
                duplicate_data = movie_data.copy()
                duplicate_data['title'] = f"{duplicate_data.get('title', 'Copy')} (Copy)"
                if 'id' in duplicate_data:
                    del duplicate_data['id']  # Remove ID for new movie
                
                success = self._create_movie_via_api(duplicate_data)
                if success:
                    st.success(f"📋 **{duplicate_data.get('title', 'Movie')}** duplicated successfully!")
                    st.session_state.show_edit_movie_modal = False
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to duplicate movie.")
            
            if update_button:
                # Validate required fields
                if not title or not genre:
                    st.error("❌ Please fill in all required fields (marked with *)")
                    return False
                
                # Process cast list
                cast_list = []
                if cast_input:
                    cast_list = [name.strip() for name in cast_input.split('\n') if name.strip()]
                
                # Prepare updated movie data
                updated_movie_data = {
                    "title": title,
                    "genre": genre,
                    "release_date": release_date.isoformat() if release_date else None,
                    "duration_minutes": duration_minutes,
                    "description": description if description else None,
                    "director": director if director else None,
                    "cast": cast_list if cast_list else None,
                    "rating": rating if rating != "Not Rated" else None,
                    "language": language,
                    "country": country,
                    "status": status
                }
                
                # Call API to update movie
                success = self._update_movie_via_api(movie_data['id'], updated_movie_data)
                
                if success:
                    st.success(f"✅ **{title}** updated successfully!")
                    st.session_state.show_edit_movie_modal = False
                    st.session_state.confirm_delete = False  # Reset delete confirmation
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to update movie. Please try again.")
        
        return False
    
    def _update_movie_via_api(self, movie_id: str, movie_data: dict) -> bool:
        """Update movie via API call"""
        try:
            import requests
            
            # API endpoint for updating movie
            api_url = f"{self.config.api.base_url}/movies/{movie_id}"
            headers = self.config.api.get_headers()
            
            # Make API call
            response = requests.put(
                api_url,
                json=movie_data,
                headers=headers,
                timeout=self.config.api.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Clear any cached data to refresh the movies list
                    if hasattr(self.api_service, 'refresh_data'):
                        self.api_service.refresh_data()
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return False
    
    def _delete_movie_via_api(self, movie_id: str) -> bool:
        """Delete movie via API call"""
        try:
            import requests
            
            # API endpoint for deleting movie
            api_url = f"{self.config.api.base_url}/movies/{movie_id}"
            headers = self.config.api.get_headers()
            
            # Make API call
            response = requests.delete(
                api_url,
                headers=headers,
                timeout=self.config.api.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Clear any cached data to refresh the movies list
                    if hasattr(self.api_service, 'refresh_data'):
                        self.api_service.refresh_data()
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return False
    
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
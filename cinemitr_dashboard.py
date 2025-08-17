import streamlit as st
from config import DashboardConfig
from api_service import APIService
from components import UIComponents

def main():
    # Initialize configuration and services
    config = DashboardConfig()
    api_service = APIService(config)
    ui = UIComponents(config, api_service)
    
    # Configure Streamlit page
    st.set_page_config(
        page_title=config.app_title,
        page_icon=config.app_icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render custom CSS
    ui.render_custom_css()
    
    # Render sidebar and get selected navigation item
    selected_page = ui.render_sidebar()
    
    # Route to appropriate page based on selection
    if selected_page == "dashboard" or selected_page is None:
        render_dashboard_page(ui, api_service)
    elif selected_page == "movies":
        render_movies_page(ui)
    elif selected_page == "content_items":
        render_content_items_page()
    elif selected_page == "upload_pipeline":
        render_upload_pipeline_page(ui)
    elif selected_page == "analytics":
        render_analytics_page()
    elif selected_page == "settings":
        render_settings_page()

def render_dashboard_page(ui: UIComponents, api_service: APIService):
    """Render the enhanced dashboard page with updated UI"""
    # Enhanced header with API info
    ui.render_header_with_api_info()
    
    # Fetch data from API
    metrics = api_service.get_dashboard_metrics()
    status_dist = api_service.get_status_distribution()
    priority_dist = api_service.get_priority_distribution()
    recent_activity = api_service.get_recent_activity()
    
    # Enhanced metrics cards with trends
    ui.render_enhanced_metrics(metrics)
    
    # Filters and action buttons
    ui.render_filters_and_actions()
    
    # File upload area
    st.markdown("---")
    ui.render_file_upload_area()
    
    # Enhanced charts section
    col_left, col_center, col_right = st.columns(3)
    
    with col_left:
        ui.render_interactive_status_chart(status_dist)
    
    with col_center:
        ui.render_priority_bar_chart(priority_dist)
    
    with col_right:
        ui.render_storage_donut_chart()
    
    # Enhanced recent activity with selection
    ui.render_enhanced_recent_activity(recent_activity)
    
    # Enhanced footer
    ui.render_footer()

def render_movies_page(ui: UIComponents = None):
    """Render enhanced movies management page with form and API integration"""
    st.header("🎬 Movies Management")
    
    # Check if edit modal should be shown
    if st.session_state.get('show_edit_movie_modal', False) and ui:
        selected_movie = st.session_state.get('selected_movie_for_edit')
        if selected_movie:
            # Render edit form as overlay
            with st.container():
                st.markdown("---")
                ui.render_edit_movie_form(selected_movie)
                st.markdown("---")
    else:
        # Normal tab-based interface
        tab1, tab2 = st.tabs(["📋 Movies List", "➕ Add New Movie"])
        
        with tab1:
            if ui:
                ui.render_movies_list_with_checkbox()
            else:
                st.info("Movies list - API integration ready")
        
        with tab2:
            if ui:
                # Render the add movie form
                movie_added = ui.render_add_movie_form()
                
                if movie_added:
                    # Switch to movies list tab after successful addition
                    st.info("Movie added! Switch to 'Movies List' tab to see the updated list.")
            else:
                st.info("Add movie form - API integration ready")
        
        # Additional functionality
        with st.expander("🔧 Advanced Options"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Import Movies", use_container_width=True):
                    st.success("📥 Bulk import functionality")
            
            with col2:
                if st.button("📊 Generate Report", use_container_width=True):
                    st.success("📊 Movies analytics report")
            
            with col3:
                if st.button("🔄 Sync with Database", use_container_width=True):
                    st.success("🔄 Database synchronization")

def render_content_items_page():
    """Render content items management page"""
    st.header("📄 Content Items Management")
    st.info("Content items page - API integration ready for content management")
    
    # Add content item management functionality here
    if st.button("Manage Content Items"):
        st.success("Content management API call would go here")

def render_upload_pipeline_page(ui: UIComponents = None):
    """Render enhanced upload pipeline page"""
    st.header("⬆️ Upload Pipeline")
    
    # Upload statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Uploads", "12", "+3")
    with col2:
        st.metric("Completed Today", "47", "+15")
    with col3:
        st.metric("Upload Rate", "67.5%", "+2.3%")
    with col4:
        st.metric("Failed Uploads", "8", "-2")
    
    # Enhanced file upload area
    if ui:
        ui.render_file_upload_area()
    else:
        # Fallback upload area
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['mp4', 'mov', 'jpg', 'jpeg', 'png']
        )
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) ready for upload")

def render_analytics_page():
    """Render analytics page"""
    st.header("📈 Analytics")
    st.info("Analytics page - API integration ready for advanced metrics")
    
    # Add analytics functionality here
    if st.button("Generate Report"):
        st.success("Analytics report API call would go here")

def render_settings_page():
    """Render settings page"""
    st.header("⚙️ Settings")
    st.info("Settings page - API integration ready for configuration management")
    
    # Add settings functionality here
    if st.button("Save Settings"):
        st.success("Settings save API call would go here")

if __name__ == "__main__":
    main()
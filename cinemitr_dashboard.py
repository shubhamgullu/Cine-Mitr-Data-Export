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
        render_movies_page()
    elif selected_page == "content_items":
        render_content_items_page()
    elif selected_page == "upload_pipeline":
        render_upload_pipeline_page()
    elif selected_page == "analytics":
        render_analytics_page()
    elif selected_page == "settings":
        render_settings_page()

def render_dashboard_page(ui: UIComponents, api_service: APIService):
    """Render the main dashboard page"""
    # Header
    ui.render_header()
    
    # Fetch data from API
    metrics = api_service.get_dashboard_metrics()
    status_dist = api_service.get_status_distribution()
    priority_dist = api_service.get_priority_distribution()
    recent_activity = api_service.get_recent_activity()
    
    # Render components
    ui.render_metrics_cards(metrics)
    
    # Charts section
    col_left, col_right = st.columns(2)
    with col_left:
        ui.render_status_chart(status_dist)
    with col_right:
        ui.render_priority_chart(priority_dist)
    
    # Recent activity
    ui.render_recent_activity(recent_activity)
    
    # Footer
    ui.render_footer()

def render_movies_page():
    """Render movies management page"""
    st.header("🎬 Movies Management")
    st.info("Movies page - API integration ready for CRUD operations")
    
    # Add movie management functionality here
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add New Movie", use_container_width=True):
            st.success("Add movie API call would go here")
    with col2:
        if st.button("Import Movies", use_container_width=True):
            st.success("Import movies API call would go here")
    with col3:
        if st.button("Export Movies", use_container_width=True):
            st.success("Export movies API call would go here")

def render_content_items_page():
    """Render content items management page"""
    st.header("📄 Content Items Management")
    st.info("Content items page - API integration ready for content management")
    
    # Add content item management functionality here
    if st.button("Manage Content Items"):
        st.success("Content management API call would go here")

def render_upload_pipeline_page():
    """Render upload pipeline page"""
    st.header("⬆️ Upload Pipeline")
    st.info("Upload pipeline page - API integration ready for file uploads")
    
    # Add upload functionality here
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' ready for upload via API")

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
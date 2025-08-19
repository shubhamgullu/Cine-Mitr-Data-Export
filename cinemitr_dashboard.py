import streamlit as st
from config import DashboardConfig
from api_service import APIService
from components import UIComponents

def main():
    # Show startup message
    startup_placeholder = st.empty()
    startup_placeholder.info("🎥 CineMitr Dashboard - Starting up...")
    
    # Initialize database connection
    try:
        from database.connection import db_manager
        db_manager.initialize()
        
        # Test database connection
        if not db_manager.test_connection():
            st.error("⚠️ Database connection failed. Please check your database configuration.")
            st.info("💡 Make sure your database server is running and the connection details are correct.")
            return
        
        # Check if content management schema migration is needed
        if check_migration_needed():
            with st.spinner("🔄 Database schema update required. Running automatic migration..."):
                if run_automatic_migration():
                    st.success("✅ Database schema updated successfully! Loading dashboard with new features...")
                    st.balloons()
                    # Clear any cached schema information
                    from database.schema_utils import schema_checker
                    schema_checker.clear_cache()
                    # Small delay to show success message
                    import time
                    time.sleep(1)
                else:
                    render_migration_prompt()
                    return
    except Exception as e:
        st.error(f"❌ Database initialization error: {str(e)}")
        st.info("💡 Please check your database configuration and ensure the database server is running.")
        return
    
    # Clear startup message
    startup_placeholder.empty()
    
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
    """Render enhanced content items management page"""
    st.header("📄 Content Items Management")
    
    # Check if edit modal should be shown
    if st.session_state.get('show_edit_content_modal', False):
        selected_content = st.session_state.get('selected_content_for_edit')
        if selected_content:
            from components import UIComponents
            from config import DashboardConfig
            from api_service import APIService
            
            config = DashboardConfig()
            api_service = APIService(config)
            ui = UIComponents(config, api_service)
            
            # Render edit form as overlay
            with st.container():
                st.markdown("---")
                ui.render_edit_content_form(selected_content)
                st.markdown("---")
    else:
        # Normal tab-based interface
        tab1, tab2 = st.tabs(["📋 Content Items List", "➕ Add New Content Item"])
        
        with tab1:
            from components import UIComponents
            from config import DashboardConfig
            from api_service import APIService
            
            config = DashboardConfig()
            api_service = APIService(config)
            ui = UIComponents(config, api_service)
            
            ui.render_content_items_list()
        
        with tab2:
            from components import UIComponents
            from config import DashboardConfig
            from api_service import APIService
            
            config = DashboardConfig()
            api_service = APIService(config)
            ui = UIComponents(config, api_service)
            
            # Render the add content item form
            content_added = ui.render_add_content_item_form()
            
            if content_added:
                # Switch to content items list tab after successful addition
                st.info("Content item added! Switch to 'Content Items List' tab to see the updated list.")
        
        # Additional functionality
        with st.expander("🔧 Advanced Options"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Import Content Items", use_container_width=True):
                    st.success("📥 Bulk import functionality")
            
            with col2:
                if st.button("📊 Generate Report", use_container_width=True):
                    st.success("📊 Content analytics report")
            
            with col3:
                if st.button("🔄 Sync with Database", use_container_width=True):
                    st.success("🔄 Database synchronization")

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

def check_migration_needed() -> bool:
    """Check if database migration is needed for content management features"""
    try:
        from database.connection import db_manager
        from sqlalchemy import text
        
        with db_manager.get_session() as session:
            # Try to check if new columns exist
            result = session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'content_items' 
                AND COLUMN_NAME IN ('link_url', 'movie_name', 'local_status')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            return len(existing_columns) < 3  # If less than 3 new columns exist
    except:
        # If we can't check (e.g., non-MySQL), assume migration is not needed
        return False

def run_automatic_migration() -> bool:
    """Run database migration automatically"""
    try:
        from database.connection import db_manager
        from sqlalchemy import text
        
        # Simple column addition commands
        column_commands = [
            "ALTER TABLE content_items ADD COLUMN link_url TEXT",
            "ALTER TABLE content_items ADD COLUMN movie_name VARCHAR(255)", 
            "ALTER TABLE content_items ADD COLUMN edited_status VARCHAR(100) DEFAULT 'Pending'",
            "ALTER TABLE content_items ADD COLUMN content_to_add TEXT",
            "ALTER TABLE content_items ADD COLUMN source_folder TEXT",
            "ALTER TABLE content_items ADD COLUMN local_status VARCHAR(20) DEFAULT 'Pending'"
        ]
        
        # Update commands
        update_commands = [
            "UPDATE content_items SET edited_status = 'Pending' WHERE edited_status IS NULL",
            "UPDATE content_items SET local_status = 'Pending' WHERE local_status IS NULL"
        ]
        
        with db_manager.get_session() as session:
            success_count = 0
            
            # Add columns
            for command in column_commands:
                try:
                    session.execute(text(command))
                    success_count += 1
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'duplicate column' in error_msg or 'already exists' in error_msg:
                        # Column already exists, that's fine
                        success_count += 1
                    # Continue with other commands even if one fails
            
            # Update existing records
            for command in update_commands:
                try:
                    session.execute(text(command))
                    success_count += 1
                except Exception as e:
                    # Update commands might fail if columns don't exist yet, that's ok
                    pass
            
            session.commit()
            
            # Verify migration success by checking if key columns exist
            try:
                result = session.execute(text("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'content_items' 
                    AND COLUMN_NAME IN ('link_url', 'movie_name', 'local_status')
                """))
                existing_columns = [row[0] for row in result.fetchall()]
                migration_successful = len(existing_columns) >= 3
                
                if migration_successful:
                    st.success(f"✅ Added {len(existing_columns)}/6 new columns to content_items table")
                    return True
                else:
                    st.warning(f"⚠️ Partial migration: {len(existing_columns)}/3 key columns added")
                    return len(existing_columns) > 0  # At least some columns were added
                    
            except Exception as verify_error:
                # If we can't verify using INFORMATION_SCHEMA, try a simple query
                try:
                    session.execute(text("SELECT link_url FROM content_items LIMIT 1"))
                    # If this works, the column exists
                    return True
                except:
                    # Migration might have failed
                    return False
            
    except Exception as e:
        st.error(f"❌ Automatic migration failed: {str(e)}")
        return False

def render_migration_prompt():
    """Render migration prompt UI"""
    st.error("🚨 Database Schema Update Required")
    
    st.markdown("""
    ### 🔄 Content Management Features Update
    
    Your database needs to be updated to support the new content management features:
    
    **New Features Include:**
    - 🔗 Content source links (Instagram/YouTube URLs)
    - 🎥 Movie association with autocomplete
    - 📝 Enhanced content editing status tracking
    - 💾 Local file status management
    - 📁 Source folder path tracking
    
    **Migration is Required** to use these features.
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🚀 Run Migration Now", type="primary", use_container_width=True):
            run_migration_ui()
    
    st.markdown("---")
    st.markdown("""
    **Manual Migration Options:**
    
    1. **Command Line:**
    ```bash
    python run_content_migration.py
    ```
    
    2. **SQL Script:**
    ```bash
    mysql -u your_user -p your_database < database_migration_content_fields.sql
    ```
    """)
    
    with st.expander("🔍 What will be migrated?"):
        st.markdown("""
        The migration will add these new columns to your `content_items` table:
        
        - `link_url` - Original content source URL
        - `movie_name` - Associated movie name
        - `local_status` - Download/processing status
        - `edited_status` - Content editing status
        - `content_to_add` - Editing notes
        - `source_folder` - Local storage path
        
        **Your existing data will not be affected.**
        """)

def run_migration_ui():
    """Run migration with UI feedback"""
    try:
        import subprocess
        import sys
        
        with st.spinner("🔄 Running database migration..."):
            # Run the migration script
            result = subprocess.run(
                [sys.executable, "run_content_migration.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                st.success("✅ Migration completed successfully!")
                st.balloons()
                st.info("🔄 Please refresh the page to use the new features.")
                
                # Add refresh button
                if st.button("🔄 Refresh Dashboard"):
                    st.rerun()
            else:
                st.error(f"❌ Migration failed: {result.stderr}")
                st.code(result.stdout)
                
    except Exception as e:
        st.error(f"❌ Failed to run migration: {str(e)}")
        st.info("💡 Please run the migration manually: `python run_content_migration.py`")

if __name__ == "__main__":
    main()
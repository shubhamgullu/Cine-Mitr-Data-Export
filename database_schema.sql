-- ================================================
-- CineMitr Database Schema
-- Compatible with MySQL Workbench
-- ================================================

-- Create database if not exists
-- CREATE DATABASE IF NOT EXISTS ui_cine_mitr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE ui_cine_mitr;

-- ================================================
-- DROP TABLES (For clean installation)
-- ================================================
SET foreign_key_checks = 0;
DROP TABLE IF EXISTS uploads;
DROP TABLE IF EXISTS analytics_metrics;
DROP TABLE IF EXISTS export_jobs;
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS content_tags;
DROP TABLE IF EXISTS movie_cast;
DROP TABLE IF EXISTS content_items;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS users;
SET foreign_key_checks = 1;

-- ================================================
-- USERS TABLE
-- ================================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role ENUM('admin', 'editor', 'viewer') NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ================================================
-- MOVIES TABLE
-- ================================================
CREATE TABLE movies (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    release_date DATE NULL,
    duration_minutes INT NULL CHECK (duration_minutes > 0),
    description TEXT NULL,
    director VARCHAR(255) NULL,
    rating VARCHAR(10) NULL,
    language VARCHAR(50) NULL,
    country VARCHAR(100) NULL,
    poster_url TEXT NULL,
    trailer_url TEXT NULL,
    status ENUM('Ready', 'Uploaded', 'In Progress', 'New', 'Failed', 'Processing') NOT NULL DEFAULT 'New',
    imdb_id VARCHAR(20) NULL,
    tmdb_id VARCHAR(20) NULL,
    box_office_collection DECIMAL(15,2) NULL,
    budget DECIMAL(15,2) NULL,
    created_by VARCHAR(36) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================
-- MOVIE CAST TABLE (Many-to-Many relationship)
-- ================================================
CREATE TABLE movie_cast (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    movie_id VARCHAR(36) NOT NULL,
    actor_name VARCHAR(255) NOT NULL,
    character_name VARCHAR(255) NULL,
    role_type ENUM('lead', 'supporting', 'cameo') NOT NULL DEFAULT 'supporting',
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);

-- ================================================
-- CONTENT ITEMS TABLE
-- ================================================
CREATE TABLE content_items (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    content_type ENUM('Movie', 'Reel', 'Trailer', 'Series', 'Documentary') NOT NULL,
    status ENUM('Ready', 'Uploaded', 'In Progress', 'New', 'Failed', 'Processing') NOT NULL DEFAULT 'New',
    priority ENUM('High', 'Medium', 'Low') NOT NULL DEFAULT 'Medium',
    description TEXT NULL,
    file_path TEXT NULL,
    file_size_bytes BIGINT NULL CHECK (file_size_bytes >= 0),
    duration_seconds INT NULL CHECK (duration_seconds >= 0),
    thumbnail_url TEXT NULL,
    video_url TEXT NULL,
    resolution VARCHAR(20) NULL,
    codec VARCHAR(50) NULL,
    bitrate INT NULL,
    frame_rate DECIMAL(5,2) NULL,
    aspect_ratio VARCHAR(20) NULL,
    quality ENUM('SD', 'HD', '4K', '8K') NULL DEFAULT 'HD',
    metadata JSON NULL,
    movie_id VARCHAR(36) NULL,
    created_by VARCHAR(36) NULL,
    uploaded_at TIMESTAMP NULL,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================
-- CONTENT TAGS TABLE (Many-to-Many relationship)
-- ================================================
CREATE TABLE content_tags (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    content_id VARCHAR(36) NOT NULL,
    tag_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE,
    UNIQUE KEY unique_content_tag (content_id, tag_name)
);

-- ================================================
-- USER SESSIONS TABLE
-- ================================================
CREATE TABLE user_sessions (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id VARCHAR(36) NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ================================================
-- UPLOADS TABLE
-- ================================================
CREATE TABLE uploads (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    upload_id VARCHAR(36) NOT NULL UNIQUE,
    file_name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes > 0),
    content_type VARCHAR(100) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    status ENUM('pending', 'uploading', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    progress_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    bytes_uploaded BIGINT NOT NULL DEFAULT 0,
    error_message TEXT NULL,
    file_path TEXT NULL,
    checksum VARCHAR(64) NULL,
    content_item_id VARCHAR(36) NULL,
    uploaded_by VARCHAR(36) NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (content_item_id) REFERENCES content_items(id) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================
-- EXPORT JOBS TABLE
-- ================================================
CREATE TABLE export_jobs (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    export_id VARCHAR(36) NOT NULL UNIQUE,
    format ENUM('csv', 'json', 'xlsx') NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    filters JSON NULL,
    file_path TEXT NULL,
    file_size_bytes BIGINT NULL,
    record_count INT NULL,
    error_message TEXT NULL,
    created_by VARCHAR(36) NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================
-- ANALYTICS METRICS TABLE
-- ================================================
CREATE TABLE analytics_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_type ENUM('count', 'size', 'percentage', 'duration', 'rate') NOT NULL,
    dimension VARCHAR(100) NULL,
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    metadata JSON NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_metric_period (metric_name, period_start, period_end)
);

-- ================================================
-- SYSTEM CONFIGURATION TABLE
-- ================================================
CREATE TABLE system_config (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    data_type ENUM('string', 'number', 'boolean', 'json') NOT NULL DEFAULT 'string',
    description TEXT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    updated_by VARCHAR(36) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================
-- AUDIT LOG TABLE
-- ================================================
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT (UUID()),
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(36) NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_values JSON NULL,
    new_values JSON NULL,
    changed_by VARCHAR(36) NULL,
    change_reason VARCHAR(255) NULL,
    ip_address VARCHAR(45) NULL,
    user_agent TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ================================================
-- PERFORMANCE INDEXES
-- ================================================

-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_created ON users(created_at);

-- Movies table indexes
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_genre ON movies(genre);
CREATE INDEX idx_movies_status ON movies(status);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_director ON movies(director);
CREATE INDEX idx_movies_language ON movies(language);
CREATE INDEX idx_movies_created_by ON movies(created_by);
CREATE INDEX idx_movies_created_at ON movies(created_at);
CREATE INDEX idx_movies_updated_at ON movies(updated_at);
CREATE FULLTEXT INDEX ft_movies_title_desc ON movies(title, description);

-- Movie cast indexes
CREATE INDEX idx_movie_cast_movie_id ON movie_cast(movie_id);
CREATE INDEX idx_movie_cast_actor ON movie_cast(actor_name);
CREATE INDEX idx_movie_cast_role_type ON movie_cast(role_type);

-- Content items indexes
CREATE INDEX idx_content_name ON content_items(name);
CREATE INDEX idx_content_type ON content_items(content_type);
CREATE INDEX idx_content_status ON content_items(status);
CREATE INDEX idx_content_priority ON content_items(priority);
CREATE INDEX idx_content_movie_id ON content_items(movie_id);
CREATE INDEX idx_content_created_by ON content_items(created_by);
CREATE INDEX idx_content_created_at ON content_items(created_at);
CREATE INDEX idx_content_updated_at ON content_items(updated_at);
CREATE INDEX idx_content_file_size ON content_items(file_size_bytes);
CREATE INDEX idx_content_duration ON content_items(duration_seconds);
CREATE INDEX idx_content_quality ON content_items(quality);
CREATE FULLTEXT INDEX ft_content_name_desc ON content_items(name, description);

-- Content tags indexes
CREATE INDEX idx_content_tags_content_id ON content_tags(content_id);
CREATE INDEX idx_content_tags_tag_name ON content_tags(tag_name);

-- User sessions indexes
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX idx_sessions_active ON user_sessions(is_active);

-- Uploads indexes
CREATE INDEX idx_uploads_upload_id ON uploads(upload_id);
CREATE INDEX idx_uploads_status ON uploads(status);
CREATE INDEX idx_uploads_content_item ON uploads(content_item_id);
CREATE INDEX idx_uploads_uploaded_by ON uploads(uploaded_by);
CREATE INDEX idx_uploads_created_at ON uploads(created_at);
CREATE INDEX idx_uploads_file_size ON uploads(file_size_bytes);

-- Export jobs indexes
CREATE INDEX idx_export_export_id ON export_jobs(export_id);
CREATE INDEX idx_export_status ON export_jobs(status);
CREATE INDEX idx_export_format ON export_jobs(format);
CREATE INDEX idx_export_created_by ON export_jobs(created_by);
CREATE INDEX idx_export_created_at ON export_jobs(created_at);

-- Analytics metrics indexes
CREATE INDEX idx_analytics_metric_name ON analytics_metrics(metric_name);
CREATE INDEX idx_analytics_metric_type ON analytics_metrics(metric_type);
CREATE INDEX idx_analytics_dimension ON analytics_metrics(dimension);
CREATE INDEX idx_analytics_recorded_at ON analytics_metrics(recorded_at);

-- System config indexes
CREATE INDEX idx_config_key ON system_config(config_key);
CREATE INDEX idx_config_public ON system_config(is_public);

-- Audit logs indexes
CREATE INDEX idx_audit_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_changed_by ON audit_logs(changed_by);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at);

-- ================================================
-- COMPOSITE INDEXES FOR COMMON QUERIES
-- ================================================

-- Content filtering and sorting
CREATE INDEX idx_content_status_type ON content_items(status, content_type);
CREATE INDEX idx_content_priority_status ON content_items(priority, status);
CREATE INDEX idx_content_type_created ON content_items(content_type, created_at DESC);

-- Movie filtering
CREATE INDEX idx_movies_genre_status ON movies(genre, status);
CREATE INDEX idx_movies_language_genre ON movies(language, genre);
CREATE INDEX idx_movies_release_status ON movies(release_date DESC, status);

-- Upload monitoring
CREATE INDEX idx_uploads_status_created ON uploads(status, created_at DESC);
CREATE INDEX idx_uploads_user_status ON uploads(uploaded_by, status);

-- Performance monitoring
CREATE INDEX idx_content_size_type ON content_items(file_size_bytes DESC, content_type);
CREATE INDEX idx_movies_duration_genre ON movies(duration_minutes, genre);

-- ================================================
-- TRIGGERS FOR AUDIT LOGGING
-- ================================================

DELIMITER //

-- Audit trigger for users table
CREATE TRIGGER tr_users_audit_insert AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, action, new_values, changed_by)
    VALUES ('users', NEW.id, 'INSERT', JSON_OBJECT(
        'username', NEW.username,
        'email', NEW.email,
        'full_name', NEW.full_name,
        'role', NEW.role,
        'is_active', NEW.is_active
    ), NEW.id);
END//

CREATE TRIGGER tr_users_audit_update AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by)
    VALUES ('users', NEW.id, 'UPDATE', 
        JSON_OBJECT(
            'username', OLD.username,
            'email', OLD.email,
            'full_name', OLD.full_name,
            'role', OLD.role,
            'is_active', OLD.is_active
        ),
        JSON_OBJECT(
            'username', NEW.username,
            'email', NEW.email,
            'full_name', NEW.full_name,
            'role', NEW.role,
            'is_active', NEW.is_active
        ), 
        NEW.id);
END//

-- Audit trigger for movies table
CREATE TRIGGER tr_movies_audit_insert AFTER INSERT ON movies
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, action, new_values, changed_by)
    VALUES ('movies', NEW.id, 'INSERT', JSON_OBJECT(
        'title', NEW.title,
        'genre', NEW.genre,
        'status', NEW.status,
        'director', NEW.director
    ), NEW.created_by);
END//

CREATE TRIGGER tr_movies_audit_update AFTER UPDATE ON movies
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by)
    VALUES ('movies', NEW.id, 'UPDATE',
        JSON_OBJECT(
            'title', OLD.title,
            'genre', OLD.genre,
            'status', OLD.status,
            'director', OLD.director
        ),
        JSON_OBJECT(
            'title', NEW.title,
            'genre', NEW.genre,
            'status', NEW.status,
            'director', NEW.director
        ),
        NEW.created_by);
END//

-- Audit trigger for content_items table
CREATE TRIGGER tr_content_audit_insert AFTER INSERT ON content_items
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, action, new_values, changed_by)
    VALUES ('content_items', NEW.id, 'INSERT', JSON_OBJECT(
        'name', NEW.name,
        'content_type', NEW.content_type,
        'status', NEW.status,
        'priority', NEW.priority
    ), NEW.created_by);
END//

CREATE TRIGGER tr_content_audit_update AFTER UPDATE ON content_items
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by)
    VALUES ('content_items', NEW.id, 'UPDATE',
        JSON_OBJECT(
            'name', OLD.name,
            'content_type', OLD.content_type,
            'status', OLD.status,
            'priority', OLD.priority
        ),
        JSON_OBJECT(
            'name', NEW.name,
            'content_type', NEW.content_type,
            'status', NEW.status,
            'priority', NEW.priority
        ),
        NEW.created_by);
END//

DELIMITER ;

-- ================================================
-- INITIAL DATA SEEDING
-- ================================================

-- Insert default admin user
INSERT INTO users (id, username, email, password_hash, full_name, role, is_active) VALUES
('admin-001', 'admin', 'admin@cinemitr.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj7VV5BVhqF.', 'CineMitr Administrator', 'admin', TRUE);

-- Insert system configuration
INSERT INTO system_config (config_key, config_value, data_type, description, is_public) VALUES
('app_name', 'CineMitr', 'string', 'Application name', TRUE),
('app_version', '1.0.0', 'string', 'Application version', TRUE),
('max_file_size_mb', '5120', 'number', 'Maximum file size in MB', FALSE),
('supported_formats', '["mp4", "avi", "mkv", "mov"]', 'json', 'Supported video formats', TRUE),
('storage_path', '/var/cinemitr/storage', 'string', 'Default storage path', FALSE),
('default_quality', 'HD', 'string', 'Default video quality', TRUE);

-- Insert sample movies
INSERT INTO movies (id, title, genre, release_date, duration_minutes, description, director, rating, language, country, status, created_by) VALUES
('movie-001', '12th Fail', 'Drama', '2023-10-27', 147, 'Based on true events, about a man who overcomes extreme hardships', 'Vidhu Vinod Chopra', '8.9', 'Hindi', 'India', 'Ready', 'admin-001'),
('movie-002', 'Pathaan', 'Action', '2023-01-25', 146, 'An action thriller featuring a secret agent', 'Siddharth Anand', '7.2', 'Hindi', 'India', 'Uploaded', 'admin-001'),
('movie-003', 'Jawan', 'Action', '2023-09-07', 169, 'A high-octane action thriller', 'Atlee', '7.8', 'Hindi', 'India', 'Ready', 'admin-001');

-- Insert movie cast
INSERT INTO movie_cast (movie_id, actor_name, character_name, role_type, order_index) VALUES
('movie-001', 'Vikrant Massey', 'Manoj Kumar Sharma', 'lead', 1),
('movie-001', 'Medha Shankar', 'Shraddha Joshi', 'lead', 2),
('movie-002', 'Shah Rukh Khan', 'Pathaan', 'lead', 1),
('movie-002', 'Deepika Padukone', 'Rubina', 'lead', 2),
('movie-002', 'John Abraham', 'Jim', 'supporting', 3),
('movie-003', 'Shah Rukh Khan', 'Azad/Vikram Rathore', 'lead', 1),
('movie-003', 'Nayanthara', 'Narmada', 'lead', 2);

-- Insert sample content items
INSERT INTO content_items (id, name, content_type, status, priority, description, file_size_bytes, duration_seconds, movie_id, created_by) VALUES
('content-001', '12th Fail Full Movie', 'Movie', 'Ready', 'High', 'Complete movie file', 2576588800, 8820, 'movie-001', 'admin-001'),
('content-002', '12th Fail Trailer', 'Trailer', 'Uploaded', 'Medium', 'Official trailer', 163840000, 180, 'movie-001', 'admin-001'),
('content-003', 'Pathaan Action Reel', 'Reel', 'Processing', 'Medium', 'Action sequence highlight', 52428800, 60, 'movie-002', 'admin-001');

-- Insert content tags
INSERT INTO content_tags (content_id, tag_name) VALUES
('content-001', 'bollywood'),
('content-001', 'drama'),
('content-001', 'inspiration'),
('content-002', 'trailer'),
('content-002', 'bollywood'),
('content-003', 'action'),
('content-003', 'reel');

-- ================================================
-- VIEWS FOR COMMON QUERIES
-- ================================================

-- Dashboard metrics view
CREATE VIEW vw_dashboard_metrics AS
SELECT 
    COUNT(DISTINCT m.id) AS total_movies,
    COUNT(c.id) AS content_items,
    COUNT(CASE WHEN c.status = 'Uploaded' THEN 1 END) AS uploaded,
    COUNT(CASE WHEN c.status IN ('New', 'In Progress') THEN 1 END) AS pending,
    ROUND(
        (COUNT(CASE WHEN c.status = 'Uploaded' THEN 1 END) * 100.0 / 
         NULLIF(COUNT(c.id), 0)), 2
    ) AS upload_rate,
    ROUND(SUM(IFNULL(c.file_size_bytes, 0)) / 1024 / 1024 / 1024, 2) AS storage_used_gb
FROM movies m
LEFT JOIN content_items c ON m.id = c.movie_id;

-- Content with movie details view
CREATE VIEW vw_content_with_movies AS
SELECT 
    c.*,
    m.title AS movie_title,
    m.genre AS movie_genre,
    m.director AS movie_director,
    m.language AS movie_language,
    GROUP_CONCAT(ct.tag_name SEPARATOR ',') AS tags
FROM content_items c
LEFT JOIN movies m ON c.movie_id = m.id
LEFT JOIN content_tags ct ON c.id = ct.content_id
GROUP BY c.id;

-- Recent activity view
CREATE VIEW vw_recent_activity AS
SELECT 
    c.id,
    c.name,
    c.content_type,
    c.status,
    c.priority,
    c.updated_at,
    m.title AS movie_title,
    u.username AS created_by_username
FROM content_items c
LEFT JOIN movies m ON c.movie_id = m.id
LEFT JOIN users u ON c.created_by = u.id
ORDER BY c.updated_at DESC
LIMIT 50;

-- Storage statistics view
CREATE VIEW vw_storage_stats AS
SELECT 
    content_type,
    COUNT(*) AS file_count,
    ROUND(SUM(file_size_bytes) / 1024 / 1024 / 1024, 2) AS total_size_gb,
    ROUND(AVG(file_size_bytes) / 1024 / 1024, 2) AS avg_size_mb,
    MIN(file_size_bytes) AS min_size_bytes,
    MAX(file_size_bytes) AS max_size_bytes
FROM content_items 
WHERE file_size_bytes IS NOT NULL
GROUP BY content_type;

-- ================================================
-- STORED PROCEDURES
-- ================================================

DELIMITER //

-- Procedure to get content statistics
CREATE PROCEDURE sp_get_content_stats(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        content_type,
        status,
        COUNT(*) AS count,
        ROUND(SUM(file_size_bytes) / 1024 / 1024 / 1024, 2) AS total_size_gb
    FROM content_items 
    WHERE created_at BETWEEN p_start_date AND p_end_date
    GROUP BY content_type, status
    ORDER BY content_type, status;
END//

-- Procedure to cleanup old uploads
CREATE PROCEDURE sp_cleanup_old_uploads(
    IN p_days_old INT,
    IN p_dry_run BOOLEAN DEFAULT TRUE
)
BEGIN
    DECLARE v_delete_count INT DEFAULT 0;
    
    IF p_dry_run THEN
        SELECT COUNT(*) AS records_to_delete
        FROM uploads 
        WHERE status IN ('failed', 'completed') 
        AND created_at < DATE_SUB(NOW(), INTERVAL p_days_old DAY);
    ELSE
        DELETE FROM uploads 
        WHERE status IN ('failed', 'completed') 
        AND created_at < DATE_SUB(NOW(), INTERVAL p_days_old DAY);
        
        SET v_delete_count = ROW_COUNT();
        SELECT v_delete_count AS deleted_records;
    END IF;
END//

-- Procedure to update content status with logging
CREATE PROCEDURE sp_update_content_status(
    IN p_content_id VARCHAR(36),
    IN p_new_status VARCHAR(50),
    IN p_updated_by VARCHAR(36)
)
BEGIN
    DECLARE v_old_status VARCHAR(50);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    SELECT status INTO v_old_status 
    FROM content_items 
    WHERE id = p_content_id;
    
    UPDATE content_items 
    SET status = p_new_status, updated_at = NOW()
    WHERE id = p_content_id;
    
    INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by)
    VALUES ('content_items', p_content_id, 'UPDATE',
        JSON_OBJECT('status', v_old_status),
        JSON_OBJECT('status', p_new_status),
        p_updated_by);
    
    COMMIT;
END//

DELIMITER ;

-- ================================================
-- PERFORMANCE OPTIMIZATION SETTINGS
-- ================================================

-- Enable query cache for better performance
-- SET GLOBAL query_cache_size = 67108864; -- 64MB
-- SET GLOBAL query_cache_type = ON;

-- Optimize InnoDB settings
-- SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB, adjust based on available RAM
-- SET GLOBAL innodb_log_file_size = 67108864; -- 64MB

-- ================================================
-- BACKUP AND MAINTENANCE RECOMMENDATIONS
-- ================================================

/*
RECOMMENDED MAINTENANCE TASKS:

1. Daily Tasks:
   - Backup database
   - Monitor disk space
   - Check error logs

2. Weekly Tasks:
   - Analyze table statistics: ANALYZE TABLE table_name;
   - Check for fragmentation: OPTIMIZE TABLE table_name;
   - Review slow query log

3. Monthly Tasks:
   - Cleanup old audit logs (older than 6 months)
   - Cleanup expired user sessions
   - Archive old export jobs
   - Update table statistics

4. Backup Commands:
   mysqldump -u username -p cinemitr_db > backup_$(date +%Y%m%d).sql
   
5. Index Maintenance:
   OPTIMIZE TABLE content_items;
   OPTIMIZE TABLE movies;
   OPTIMIZE TABLE uploads;
*/

-- ================================================
-- SCHEMA VERSION TRACKING
-- ================================================

INSERT INTO system_config (config_key, config_value, data_type, description, is_public) VALUES
('schema_version', '1.0.0', 'string', 'Database schema version', FALSE),
('schema_created_at', NOW(), 'string', 'Schema creation timestamp', FALSE);

-- ================================================
-- END OF SCHEMA
-- ================================================
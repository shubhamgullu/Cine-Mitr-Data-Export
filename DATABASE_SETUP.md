# CineMitr Database Setup Guide

This guide explains how to set up the database for the CineMitr Content Management System.

## Prerequisites

1. **MySQL Server** (8.0 or higher recommended)
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use Docker: `docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 mysql:8.0`

2. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup Steps

### 1. Create Database

Connect to MySQL and create the database:

```sql
CREATE DATABASE ui_cine_mitr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure Environment

Copy the example environment file and update with your database credentials:

```bash
cp .env.example .env
```

Edit `.env` file with your database settings:

```env
DATABASE_DRIVER=mysql+pymysql
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
DATABASE_NAME=ui_cine_mitr
DATABASE_USER=root
DATABASE_PASSWORD=your_password_here
DATABASE_DEBUG=false
```

### 3. Initialize Database Schema

Run the database initialization script:

```bash
python init_database.py
```

This will:
- Create all necessary tables
- Set up indexes for performance
- Create audit triggers
- Insert initial configuration data
- Add sample data for testing

### 4. Verify Setup

Test the database integration:

```bash
python test_database.py
```

This will run comprehensive tests to ensure:
- Database connection works
- CRUD operations function correctly
- API endpoints can interact with the database
- Dashboard metrics are calculated properly

## Database Schema Overview

The database includes the following main tables:

### Core Tables
- `users` - User accounts and authentication
- `movies` - Movie catalog with metadata
- `movie_cast` - Actor-movie relationships
- `content_items` - All content (movies, trailers, reels)
- `content_tags` - Tagging system

### Operational Tables
- `uploads` - File upload tracking
- `export_jobs` - Data export management
- `user_sessions` - Session management
- `analytics_metrics` - Performance metrics

### System Tables
- `system_config` - Application configuration
- `audit_logs` - Change tracking and auditing

## Starting the Application

Once the database is set up, you can start the API server:

```bash
python main.py
```

And the Streamlit dashboard:

```bash
streamlit run cinemitr_dashboard.py
```

## Database Management

### Backup Database
```bash
mysqldump -u root -p ui_cine_mitr > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
mysql -u root -p ui_cine_mitr < backup_file.sql
```

### View Database Status
```sql
USE ui_cine_mitr;
SELECT COUNT(*) as movie_count FROM movies;
SELECT COUNT(*) as content_count FROM content_items;
SELECT status, COUNT(*) as count FROM content_items GROUP BY status;
```

## Troubleshooting

### Connection Issues
1. Verify MySQL is running: `sudo systemctl status mysql`
2. Check credentials in `.env` file
3. Ensure database exists: `SHOW DATABASES;`
4. Check user permissions: `SHOW GRANTS FOR 'root'@'localhost';`

### Performance Issues
1. Review slow query log
2. Run `ANALYZE TABLE` for statistics
3. Check index usage with `EXPLAIN` queries
4. Monitor storage space

### Data Issues
1. Check audit logs for changes: `SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;`
2. Verify foreign key constraints
3. Check for orphaned records

## Development Notes

- The database uses UUIDs for primary keys for better scalability
- All timestamps are stored in UTC
- JSON columns are used for flexible metadata storage
- Audit triggers automatically track changes
- Indexes are optimized for common query patterns

## Production Considerations

1. **Security**
   - Use strong passwords
   - Enable SSL connections
   - Regular security updates
   - Monitor access logs

2. **Performance**
   - Configure InnoDB buffer pool size
   - Set up read replicas if needed
   - Monitor slow queries
   - Regular maintenance tasks

3. **Backup**
   - Automated daily backups
   - Test restore procedures
   - Keep multiple backup generations
   - Store backups securely

4. **Monitoring**
   - Set up alerting for disk space
   - Monitor connection counts
   - Track query performance
   - Monitor replication lag (if applicable)
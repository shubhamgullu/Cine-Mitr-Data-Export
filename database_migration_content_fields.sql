-- Migration script to add new fields to content_items table
-- Run this script to update the database schema for enhanced content management

-- Add new columns to content_items table
ALTER TABLE content_items 
ADD COLUMN IF NOT EXISTS link_url TEXT COMMENT 'Original source URL (e.g., Instagram reel URL)',
ADD COLUMN IF NOT EXISTS movie_name VARCHAR(255) COMMENT 'Movie name for content association',
ADD COLUMN IF NOT EXISTS edited_status VARCHAR(100) DEFAULT 'Pending' COMMENT 'Edit status (Basic Crop, etc.)',
ADD COLUMN IF NOT EXISTS content_to_add TEXT COMMENT 'Notes about content editing needs',
ADD COLUMN IF NOT EXISTS source_folder TEXT COMMENT 'Source folder path for downloaded content';

-- Add local_status enum type and column
-- Note: This may vary depending on your database system (MySQL, PostgreSQL, etc.)

-- For MySQL:
ALTER TABLE content_items 
ADD COLUMN IF NOT EXISTS local_status ENUM('Downloaded', 'Processing', 'Ready', 'Failed', 'Pending') DEFAULT 'Pending';

-- For PostgreSQL (uncomment if using PostgreSQL):
-- CREATE TYPE local_status_types AS ENUM ('Downloaded', 'Processing', 'Ready', 'Failed', 'Pending');
-- ALTER TABLE content_items ADD COLUMN IF NOT EXISTS local_status local_status_types DEFAULT 'Pending';

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_content_items_movie_name ON content_items(movie_name);
CREATE INDEX IF NOT EXISTS idx_content_items_local_status ON content_items(local_status);
CREATE INDEX IF NOT EXISTS idx_content_items_edited_status ON content_items(edited_status);
CREATE INDEX IF NOT EXISTS idx_content_items_link_url ON content_items(link_url(255)); -- For TEXT columns, specify length

-- Add index on movies table for autocomplete functionality
CREATE INDEX IF NOT EXISTS idx_movies_title_search ON movies(title);

-- Update existing records with default values if needed
UPDATE content_items 
SET edited_status = 'Pending' 
WHERE edited_status IS NULL;

UPDATE content_items 
SET local_status = 'Pending' 
WHERE local_status IS NULL;

-- Optional: Add foreign key constraint if movie_name should reference movies.title
-- ALTER TABLE content_items ADD CONSTRAINT fk_content_movie_name 
-- FOREIGN KEY (movie_name) REFERENCES movies(title) ON DELETE SET NULL ON UPDATE CASCADE;

COMMIT;
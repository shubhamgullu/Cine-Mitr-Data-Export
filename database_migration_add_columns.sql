-- Migration script to add is_available and location columns to movies table
-- Run this script to update existing database schema

USE ui_cine_mitr;

-- Add new columns to movies table
ALTER TABLE movies 
ADD COLUMN is_available BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Whether the movie is available';

ALTER TABLE movies 
ADD COLUMN location TEXT NULL COMMENT 'Local file path for the movie file';

-- Update existing movies to have default values
UPDATE movies SET is_available = TRUE WHERE is_available IS NULL;

-- Verify the changes
DESCRIBE movies;

-- Check current movies data
SELECT id, title, is_available, location FROM movies LIMIT 10;

-- Optional: Add index for is_available for better query performance
CREATE INDEX idx_movies_is_available ON movies(is_available);

-- Optional: Add index for location for file path searches (first 255 chars)
CREATE INDEX idx_movies_location ON movies(location(255));

SELECT 'Migration completed successfully!' as status;
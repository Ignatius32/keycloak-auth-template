-- Initial database setup for Docker deployment
-- This file is automatically executed when PostgreSQL container starts

-- Create the main application database (if not created by POSTGRES_DB)
-- The main database is usually created by the POSTGRES_DB environment variable

-- You can add additional setup here if needed
-- For example, extensions or additional databases

-- Extensions that might be useful
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\echo 'Database initialization completed successfully!'

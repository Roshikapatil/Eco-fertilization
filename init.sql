-- Database initialization script for Crop Recommendation System
-- This script is used by Docker Compose to initialize the MySQL database

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS crop_recommendation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE crop_recommendation;

-- Create user if it doesn't exist
CREATE USER IF NOT EXISTS 'crop_user'@'%' IDENTIFIED BY 'crop_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON crop_recommendation.* TO 'crop_user'@'%';

-- Flush privileges
FLUSH PRIVILEGES;

-- Create indexes for better performance (will be created by Django migrations)
-- These are just examples of what Django will create

-- Show tables (for verification)
SHOW TABLES;

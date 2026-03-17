CREATE DATABASE IF NOT EXISTS crime_db;
USE crime_db;

DROP TABLE IF EXISTS crimes;
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS crimes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crime_id VARCHAR(50) UNIQUE,
    crime_type VARCHAR(100) NOT NULL,
    description TEXT,
    occurrence_date DATETIME,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location_description VARCHAR(255),
    arrestED BOOLEAN DEFAULT FALSE,
    domestic BOOLEAN DEFAULT FALSE,
    district INT,
    ward INT,
    community_area INT,
    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'officer') NOT NULL DEFAULT 'officer',
    station VARCHAR(100),
    badge_number VARCHAR(50),
    aadhar_number VARCHAR(12),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ANPR System - Database Setup
-- Run this in MySQL before starting the application

CREATE DATABASE IF NOT EXISTS vehicle_db;

USE vehicle_db;

CREATE TABLE IF NOT EXISTS vehicle_info (
    registration VARCHAR(20)  NOT NULL PRIMARY KEY,
    owner_name   VARCHAR(100) NOT NULL,
    house_name   VARCHAR(100),
    place        VARCHAR(100),
    phone        VARCHAR(15)
);

-- Sample entries (Indian format plates)
INSERT INTO vehicle_info (registration, owner_name, house_name, place, phone) VALUES
    ('KL07AB1234', 'Rahul Menon',    'Manorama House', 'Ernakulam', '9876543210'),
    ('KL10CD5678', 'Priya Nair',     'Rose Cottage',   'Thrissur',  '9123456789'),
    ('KL01EF9012', 'Anoop Kumar',    'Green Villa',    'Trivandrum','9845001234');

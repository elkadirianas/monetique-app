
CREATE TABLE fact_transactions (
    id SERIAL PRIMARY KEY,
    iface VARCHAR(10),
    ts TIMESTAMP,
    status VARCHAR(16),
    amount NUMERIC(12,2),
    etl_loaded_at TIMESTAMP DEFAULT now()
);

-- Users table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    hashed_password VARCHAR(128) NOT NULL,
    role VARCHAR(16) DEFAULT 'user'
);

-- Insert initial admin user (password: admin, hashed with bcrypt)
INSERT INTO users (username, hashed_password, role)
VALUES ('admin', '$2b$12$SRDtelb/jCLm30L5RqkLgeEMykC5zMMONidV55IFrTsMqv8ePbCaq', 'admin');

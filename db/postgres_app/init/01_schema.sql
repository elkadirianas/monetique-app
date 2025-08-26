CREATE TABLE fact_transactions (
    id SERIAL PRIMARY KEY,
    iface VARCHAR(10),
    ts TIMESTAMP,
    status VARCHAR(16),
    amount NUMERIC(12,2),
    etl_loaded_at TIMESTAMP DEFAULT now()
);

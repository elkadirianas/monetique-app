CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    iface VARCHAR(10),
    ts TIMESTAMP DEFAULT now(),
    status VARCHAR(16), -- ACCEPTED / REJECT_TECH / REJECT_FUNC
    amount NUMERIC(12,2)
);

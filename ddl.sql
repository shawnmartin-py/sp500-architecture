DROP TABLE IF EXISTS price;
CREATE TABLE IF NOT EXISTS price(
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    price FLOAT,
    extracted_time TIMESTAMP
);
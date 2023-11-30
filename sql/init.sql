CREATE TABLE energy_usage (
    device VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    power real NOT NULL,
    avg_mg_co2 real,
    PRIMARY KEY (device, timestamp)
);
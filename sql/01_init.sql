CREATE TABLE IF NOT EXISTS energy_usage (
    device VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    power_draw_watts real NOT NULL,
    avg_emitted_mgco2e real,
    grid_carbon_intensity_gco2perkwhr real,
    PRIMARY KEY (device, timestamp)
);

CREATE OR REPLACE VIEW energy_usage_view AS
SELECT *
FROM energy_usage
ORDER BY timestamp DESC
LIMIT 100000;

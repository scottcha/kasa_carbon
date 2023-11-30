#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE "$VIEW_USER" WITH LOGIN PASSWORD '$VIEW_USER_PASSWORD';
    GRANT SELECT ON energy_usage_view TO "$VIEW_USER";
EOSQL

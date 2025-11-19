-- Enable PostGIS extension for geolocation features
-- This is executed automatically when the database container starts
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify PostGIS installation
SELECT PostGIS_version();

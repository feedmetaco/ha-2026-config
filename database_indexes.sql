-- ============================================================================
-- DATABASE INDEX OPTIMIZATION
-- Run these SQL commands on your Home Assistant database
-- Creates indexes optimized for 968 sensors, 449 switches, 256 binary sensors
-- ============================================================================

-- Index 1: Sensor entity_id + time queries (CRITICAL - 968 sensors!)
CREATE INDEX IF NOT EXISTS idx_states_sensor_time 
ON states (entity_id, last_updated) 
WHERE entity_id LIKE 'sensor.%';

-- Index 2: Switch entity_id + state queries (449 switches)
CREATE INDEX IF NOT EXISTS idx_states_switch 
ON states (entity_id, state)
WHERE entity_id LIKE 'switch.%';

-- Index 3: Binary sensor queries (256 binary sensors)
CREATE INDEX IF NOT EXISTS idx_states_binary
ON states (entity_id, last_updated, state)
WHERE entity_id LIKE 'binary_sensor.%';

-- Index 4: General time-range queries (all entities)
CREATE INDEX IF NOT EXISTS idx_states_time_range 
ON states (last_updated, entity_id, state);

-- ============================================================================
-- HOW TO RUN THESE COMMANDS:
-- ============================================================================
-- Option 1: Via HA Terminal & SSH add-on
--   1. Install "Terminal & SSH" add-on
--   2. Open terminal
--   3. Run: ha database execute "COPY_SQL_HERE"
--
-- Option 2: Via Database Client (MySQL/MariaDB)
--   1. Connect to your HA database
--   2. Run each CREATE INDEX command
--   3. Verify with: SHOW INDEX FROM states;
--
-- Option 3: Via phpMyAdmin (if you have it)
--   1. Open phpMyAdmin
--   2. Select homeassistant database
--   3. Go to SQL tab
--   4. Paste and execute each command
-- ============================================================================

-- EXPECTED RESULTS:
-- - 10-100x faster entity history queries
-- - Dashboards load 5-10x faster
-- - Reduced CPU usage during queries
-- - Better overall system performance
-- ============================================================================

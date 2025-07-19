--- UP
ALTER TABLE events ADD COLUMN eventType TEXT DEFAULT('party');

--- DOWN
ALTER TABLE events DROP COLUMN eventType;
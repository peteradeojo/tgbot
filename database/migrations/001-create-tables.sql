--- UP
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    userId VARCHAR NOT NULL,
    createdAt DATE
);

CREATE TABLE IF NOT EXISTS events(
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    userId INTEGER NOT NULL,
    eventDate DATE,
    eventTime TIME,
    createdAt DATE NOT NULL,
    updatedAt DATE
);
--- DOWN
DROP TABLE users;
DROP TABLE events;
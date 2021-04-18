CREATE TABLE do_session (
    id INTEGER PRIMARY KEY,
    mode TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL,
    actual_end_time TIMESTAMP
);

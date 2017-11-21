"""
Creates empty database

References
    https://docs.python.org/3.6/library/sqlite3.html
    https://www.sqlite.org/
"""

import sqlite3
import os.path

sqlite_file = '../../data/databases/booking_database.db'

if os.path.isfile(sqlite_file):
    raise IOError('Database file "' + sqlite_file + '" already exists. Database should be created in a new file.')

conn = sqlite3.connect(sqlite_file)

with conn: # conn.commit() is called if next statements execute successfully
    # Enforce foreign key constraints while this connection is open.
    # Must be executed for each new connection
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.executescript("""
        
        CREATE TABLE counties(
            county_name     TEXT PRIMARY KEY NOT NULL,
            current_roster  INTEGER NOT NULL,
            release_info    INTEGER NOT NULL,
            stale_days      INTEGER,
            expire_days     INTEGER,
            stale_events    TEXT,
            expire_events   TEXT
        );
        
        CREATE TABLE bookings(
            booking_id          INTEGER PRIMARY KEY NOT NULL,
            booking_timestamp   TEXT NOT NULL,
            release_timestamp   TEXT,
            county_name         TEXT NOT NULL,
            url                 TEXT,
            processing_numbers  TEXT,
            facility            TEXT,
            other               TEXT,
            notes               TEXT,        
            FOREIGN KEY(county_name) REFERENCES counties(county_name)
        );
        
        CREATE TABLE inmates(
            booking_id          INTEGER PRIMARY KEY NOT NULL,
            inmate_id           TEXT,
            inmate_lastname     TEXT,
            inmate_firstname    TEXT,
            inmate_middlename   TEXT,
            inmate_sex          TEXT,
            inmate_race         TEXT,
            inmate_age          INTEGER,
            inmate_dob          TEXT,
            inmate_address      TEXT,
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
        );
        
        CREATE TABLE charges(
            booking_id      INTEGER NOT NULL,
            charge_number   INTEGER NOT NULL,
            agency          TEXT,
            charges         TEXT,
            severity        TEXT,
            current_status  TEXT,
            court_dates     TEXT,
            PRIMARY KEY (booking_id, charge_number),
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
        );
        
        CREATE TABLE bonds(
            booking_id      INTEGER NOT NULL,
            charge_number   INTEGER,
            bond_amount     TEXT,
            bond_text       TEXT,
            PRIMARY KEY (booking_id, charge_number),
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id),
            FOREIGN KEY(booking_id, charge_number) REFERENCES charges(booking_id, charge_number)
        );
        
        CREATE TABLE timelines(
            booking_id          INTEGER PRIMARY KEY NOT NULL,
            timestamp           TEXT NOT NULL,
            event               TEXT NOT NULL,
            notes               TEXT,
            days_jailed         TEXT,
            total_days_jailed   TEXT,
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
        );
    """)

conn.close()

print('Done initializing database stored in "' + sqlite_file + '"')


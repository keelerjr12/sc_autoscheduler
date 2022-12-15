DROP TABLE pilots_quals;
DROP TABLE quals;
DROP TABLE pilots;

CREATE TABLE IF NOT EXISTS pilots (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    prsn_id         integer,
    last_name       varchar,
    first_name      varchar
);

CREATE TABLE IF NOT EXISTS quals (
    id              SERIAL PRIMARY KEY,
    name            varchar
);

CREATE TABLE IF NOT EXISTS pilots_quals (
    pilot_id        INT REFERENCES pilots(id) NOT NULL,
    qual_id         INT REFERENCES quals(id) NOT NULL,
    PRIMARY KEY     (pilot_id, qual_id)
);

INSERT INTO pilots (auth_group_id, prsn_id, last_name, first_name) VALUES (1, 1, 'Keeler', 'Joshua'), (1, 2, 'Moore', 'Gary');

INSERT INTO quals (name) VALUES ('Operations Supervisor'), ('SOF'), ('RSU Controller'), ('RSU Observer');

INSERT INTO pilots_quals(pilot_id, qual_id) VALUES (1, 1), (2, 3), (2, 4);
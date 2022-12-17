DROP TABLE pilots_orgs;
DROP TABLE orgs;
DROP TABLE pilots_quals;
DROP TABLE quals;
DROP TABLE pilots;

CREATE TABLE IF NOT EXISTS pilots (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    prsn_id         INT,
    last_name       VARCHAR NOT NULL,
    first_name      VARCHAR NOT NULL,
    ausm_tier       INT NOT NULL
);

CREATE TABLE IF NOT EXISTS quals (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS pilots_quals (
    pilot_id        INT REFERENCES pilots(id) NOT NULL,
    qual_id         INT REFERENCES quals(id) NOT NULL,
    PRIMARY KEY     (pilot_id, qual_id)
);

CREATE TABLE IF NOT EXISTS orgs (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS pilots_orgs (
    pilot_id        INT REFERENCES pilots(id) NOT NULL,
    org_id          INT REFERENCES orgs(id) NOT NULL,
    PRIMARY KEY     (pilot_id, org_id)
);

INSERT INTO pilots (auth_group_id, prsn_id, last_name, first_name, ausm_tier) VALUES (1, 1, 'Keeler', 'Joshua', 3), (1, 2, 'Moore', 'Gary', 2);

INSERT INTO quals (name) VALUES ('Operations Supervisor'), ('SOF'), ('RSU Controller'), ('RSU Observer'), ('PIT IP');

INSERT INTO pilots_quals(pilot_id, qual_id) VALUES (1, 1), (2, 3), (2, 4);

INSERT INTO orgs (name) VALUES ('M'), ('N'), ('O'), ('P'), ('X');

INSERT INTO pilots_orgs VALUES (1, 3);
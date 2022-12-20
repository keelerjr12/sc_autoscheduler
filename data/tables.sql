DROP TABLE pilots_orgs CASCADE;
DROP TABLE orgs CASCADE;
DROP TABLE pilots_quals CASCADE;
DROP TABLE quals CASCADE;
DROP TABLE pilots CASCADE;

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

CREATE TEMPORARY TABLE t (
    auth_group_id INT NOT NULL, 
    last_name VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    prsn_id INT PRIMARY KEY,
    grade VARCHAR NOT NULL,
    qual_code VARCHAR NOT NULL,
    nation VARCHAR NOT NULL,
    unit VARCHAR NOT NULL,
    ip_date VARCHAR,
    bip VARCHAR,
    exp_inexp VARCHAR,
    wx_cat INT,
    rsu_observer VARCHAR,
    rsu_controller VARCHAR,
    sof VARCHAR,
    ops_supervisor VARCHAR,
    check_pilot VARCHAR,
    ipc_pilot VARCHAR,
    fpc_pilot VARCHAR,
    fcf_pilot VARCHAR,
    pit_ip VARCHAR,
    sefe VARCHAR,
    stall_pilot VARCHAR,
    flt_ld_4ship VARCHAR,
    wg_4ship VARCHAR,
    rnav VARCHAR,
    h2g VARCHAR,
    night VARCHAR,
    msi VARCHAR,
    sgto VARCHAR,
    ausm_tier INT,
    assigned_org VARCHAR
);

\COPY t FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/lox.csv' delimiter ',' CSV HEADER; 

INSERT INTO pilots (auth_group_id, prsn_id, last_name, first_name, ausm_tier) SELECT auth_group_id, prsn_id, last_name, first_name, ausm_tier FROM t;

INSERT INTO quals (name) VALUES ('Operations Supervisor'), ('SOF'), ('RSU Controller'), ('RSU Observer'), ('PIT IP');

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    t
JOIN    pilots
ON      pilots.prsn_id = t.prsn_id
JOIN    quals
ON      quals.name = 'Operations Supervisor'
AND     t.ops_supervisor = 'X';

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    t
JOIN    pilots
ON      pilots.prsn_id = t.prsn_id
JOIN    quals
ON      quals.name = 'SOF'
AND    (t.sof = 'X'
OR     t.sof = 'X*'
OR     t.sof = 'D'
OR     t.sof = 'D*');

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    t
JOIN    pilots
ON      pilots.prsn_id = t.prsn_id
JOIN    quals
ON      quals.name = 'RSU Controller'
AND    (t.rsu_controller = 'X'
OR     t.rsu_controller = 'X*'
OR     t.rsu_controller = 'D'
OR     t.rsu_controller = 'D*');

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    t
JOIN    pilots
ON      pilots.prsn_id = t.prsn_id
JOIN    quals
ON      quals.name = 'RSU Observer'
AND    (t.rsu_observer = 'X'
OR     t.rsu_observer = 'X*'
OR     t.rsu_observer = 'D'
OR     t.rsu_observer = 'D*');

INSERT INTO orgs (name) VALUES ('M'), ('N'), ('O'), ('P'), ('X');

INSERT INTO pilots_orgs 
SELECT  pilots.id, orgs.id
FROM    t
JOIN    pilots
ON      pilots.prsn_id = t.prsn_id
JOIN    orgs
ON      orgs.name = t.assigned_org;

DROP TABLE t;
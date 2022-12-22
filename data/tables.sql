DROP TABLE pilots_orgs CASCADE;
DROP TABLE pilots_quals CASCADE;
DROP TABLE quals CASCADE;
DROP TABLE qual_types CASCADE;
DROP TABLE pilots CASCADE;

DROP TABLE shell_lines CASCADE;

DROP TABLE orgs CASCADE;

CREATE TABLE IF NOT EXISTS pilots (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    prsn_id         INT,
    last_name       VARCHAR NOT NULL,
    first_name      VARCHAR NOT NULL,
    ausm_tier       INT NOT NULL
);

CREATE TABLE IF NOT EXISTS qual_types (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS quals (
    id              SERIAL PRIMARY KEY,
    type_id         INT REFERENCES qual_types(id) NOT NULL, 
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

CREATE TABLE IF NOT EXISTS shell_lines (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    num             INT NOT NULL, 
    start_date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    org_id          INT REFERENCES orgs(id),
    fly_go          INT NOT NULL
);

CREATE TEMPORARY TABLE tmp_personnel (
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

\COPY tmp_personnel FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/lox.csv' delimiter ',' CSV HEADER; 

INSERT INTO pilots (auth_group_id, prsn_id, last_name, first_name, ausm_tier) SELECT auth_group_id, prsn_id, last_name, first_name, ausm_tier FROM tmp_personnel;

INSERT INTO qual_types (name) VALUES ('Duty'), ('Flight');
INSERT INTO quals (type_id, name) VALUES (1, 'Operations Supervisor'), (1, 'SOF'), (1, 'RSU Controller'), (1, 'RSU Observer'), (2, 'PIT IP');

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    tmp_personnel
JOIN    pilots
ON      pilots.prsn_id = tmp_personnel.prsn_id
JOIN    quals
ON      quals.name = 'Operations Supervisor'
AND     tmp_personnel.ops_supervisor = 'X';

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    tmp_personnel
JOIN    pilots
ON      pilots.prsn_id = tmp_personnel.prsn_id
JOIN    quals
ON      quals.name = 'SOF'
AND    (tmp_personnel.sof = 'X'
OR     tmp_personnel.sof = 'X*'
OR     tmp_personnel.sof = 'D'
OR     tmp_personnel.sof = 'D*');

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    tmp_personnel
JOIN    pilots
ON      pilots.prsn_id = tmp_personnel.prsn_id
JOIN    quals
ON      quals.name = 'RSU Controller'
AND    (tmp_personnel.rsu_controller = 'X'
OR     tmp_personnel.rsu_controller = 'X*'
OR     tmp_personnel.rsu_controller = 'D'
OR     tmp_personnel.rsu_controller = 'D*');

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    tmp_personnel
JOIN    pilots
ON      pilots.prsn_id = tmp_personnel.prsn_id
JOIN    quals
ON      quals.name = 'RSU Observer'
AND    (tmp_personnel.rsu_observer = 'X'
OR     tmp_personnel.rsu_observer = 'X*'
OR     tmp_personnel.rsu_observer = 'D'
OR     tmp_personnel.rsu_observer = 'D*');

INSERT INTO pilots_quals
SELECT  pilots.id, quals.id
FROM    tmp_personnel
JOIN    pilots
ON      pilots.prsn_id = tmp_personnel.prsn_id
JOIN    quals
ON      quals.name = 'PIT IP'
AND     tmp_personnel.pit_ip = 'X';

INSERT INTO orgs (name) VALUES ('M'), ('N'), ('O'), ('P'), ('X');

INSERT INTO pilots_orgs 
SELECT  pilots.id, orgs.id
FROM    tmp_personnel
JOIN    pilots
ON      pilots.prsn_id = tmp_personnel.prsn_id
JOIN    orgs
ON      orgs.name = tmp_personnel.assigned_org;

DROP TABLE tmp_personnel;

CREATE TEMPORARY TABLE tmp_lines (
    auth_group_id   INT NOT NULL, 
    num             INT NOT NULL,
    start_date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    org_name        VARCHAR,
    tof_event       VARCHAR,
    fly_go          INT NOT NULL 
);

\COPY tmp_lines FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/flying_schedule.csv' delimiter ',' CSV HEADER; 

INSERT INTO shell_lines (auth_group_id, num, start_date_time, org_id, fly_go) 
    SELECT auth_group_id, num, start_date_time, orgs.id, fly_go 
    FROM tmp_lines 
    JOIN orgs 
    ON orgs.name = SUBSTRING(tmp_lines.org_name, POSITION('- ' IN tmp_lines.org_name)+2, 1)
    ORDER BY start_date_time, num;

DROP TABLE tmp_lines;
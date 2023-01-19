DROP TABLE absence_request CASCADE;

DROP TABLE pilot_org CASCADE;
DROP TABLE pilot_qual CASCADE;
DROP TABLE qual CASCADE;
DROP TABLE qual_type CASCADE;

DROP TABLE person_line CASCADE;
DROP TABLE person CASCADE;

DROP TABLE shell_line CASCADE;
DROP TABLE shell_duty CASCADE;

DROP TABLE duty CASCADE;
DROP TABLE duty_type CASCADE;

DROP TABLE org CASCADE;

DROP TABLE schedule CASCADE;

CREATE TABLE IF NOT EXISTS person (
    id              SERIAL PRIMARY KEY,
    tims_id         int NOT NULL,
    last_name       VARCHAR,
    first_name      VARCHAR,
    middle_name     VARCHAR
);

CREATE TABLE IF NOT EXISTS person_line (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    person_id       INT REFERENCES person(id) NOT NULL,
    ausm_tier       INT NOT NULL DEFAULT 4
);

CREATE TABLE IF NOT EXISTS qual_type (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS qual (
    id              SERIAL PRIMARY KEY,
    type_id         INT REFERENCES qual_type(id) NOT NULL, 
    name            VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS pilot_qual (
    person_line_id   INT REFERENCES person_line(id) NOT NULL,
    qual_id         INT REFERENCES qual(id) NOT NULL,
    PRIMARY KEY     (person_line_id, qual_id)
);

CREATE TABLE IF NOT EXISTS org (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS pilot_org (
    person_line_id   INT REFERENCES person_line(id) NOT NULL,
    org_id          INT REFERENCES org(id) NOT NULL,
    PRIMARY KEY     (person_line_id, org_id)
);

CREATE TABLE IF NOT EXISTS shell_line (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    num             INT NOT NULL, 
    start_date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    org_id          INT REFERENCES org(id),
    fly_go          INT NOT NULL
);

CREATE TABLE IF NOT EXISTS duty_type (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    name            VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS duty (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    duty_type_id    INT REFERENCES duty_type(id) NOT NULL,
    name            VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS shell_duty (
    id              SERIAL PRIMARY KEY,
    auth_group_id   INT REFERENCES auth_group(id) NOT NULL,
    duty_id         INT REFERENCES duty(id) NOT NULL,
    start_date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_date_time   TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS absence_request (
    id                      SERIAL PRIMARY KEY,
    person_id               INT REFERENCES person(id) NOT NULL,
    reason                  VARCHAR(1024),
    start_date_time         TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_date_time           TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    occur_start_date_time   TIMESTAMP WITHOUT TIME ZONE,
    occur_end_date_time     TIMESTAMP WITHOUT TIME ZONE,
    day_of_week_ptn         INT
);

CREATE TABLE IF NOT EXISTS schedule (
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR NOT NULL, 
    start_date              DATE,
    end_date                DATE,
    submission_date_time    TIMESTAMP WITHOUT TIME ZONE,
    status                  VARCHAR NOT NULL
);

CREATE TEMPORARY TABLE tmp_person (
    prsn_id INT PRIMARY KEY,
    last_name VARCHAR,
    first_name VARCHAR,
    middle_name VARCHAR
);

CREATE TEMPORARY TABLE tmp_lox_person (
    auth_group_id INT,
    last_name VARCHAR,
    first_name VARCHAR,
    prsn_id INT PRIMARY KEY,
    grade VARCHAR,
    qual_code VARCHAR,
    nation VARCHAR,
    unit VARCHAR,
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

\COPY tmp_person FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/personnel.csv' delimiter ',' CSV HEADER; 
INSERT INTO person (tims_id, last_name, first_name, middle_name) SELECT prsn_id, last_name, first_name, middle_name FROM tmp_person;

\COPY tmp_lox_person FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/lox.csv' delimiter ',' CSV HEADER; 

INSERT INTO person_line (auth_group_id, person_id, ausm_tier) 
    SELECT auth_group_id, person.id, ausm_tier 
    FROM tmp_lox_person
    JOIN person
    ON   person.tims_id = prsn_id;

INSERT INTO qual_type (name) VALUES ('Duty'), ('Flight');
INSERT INTO qual (type_id, name) 
VALUES 
    (1, 'Operations Supervisor'), 
    (1, 'SOF'), 
    (1, 'RSU Controller'), 
    (1, 'RSU Observer'), 
    (2, 'IPC Pilot'),
    (2, 'FPC Pilot'),
    (2, 'FCF Pilot'),
    (2, 'PIT IP'),
    (2, 'SEFE');

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'Operations Supervisor'
    AND         tmp_lox_person.ops_supervisor = 'X';

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'SOF'
    AND         (tmp_lox_person.sof = 'X'
    OR          tmp_lox_person.sof = 'X*'
    OR          tmp_lox_person.sof = 'D'
    OR          tmp_lox_person.sof = 'D*');

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'RSU Controller'
    AND         (tmp_lox_person.rsu_controller = 'X'
    OR          tmp_lox_person.rsu_controller = 'X*'
    OR          tmp_lox_person.rsu_controller = 'D'
    OR          tmp_lox_person.rsu_controller = 'D*');

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'RSU Observer'
    AND         (tmp_lox_person.rsu_observer = 'X'
    OR          tmp_lox_person.rsu_observer = 'X*'
    OR          tmp_lox_person.rsu_observer = 'D'
    OR          tmp_lox_person.rsu_observer = 'D*');

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'IPC Pilot'
    AND         (tmp_lox_person.ipc_pilot = 'X'
    OR          tmp_lox_person.ipc_pilot = 'P'
    OR          tmp_lox_person.ipc_pilot = 'U');

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'FPC Pilot'
    AND         (tmp_lox_person.fpc_pilot = 'X'
    OR          tmp_lox_person.fpc_pilot = 'P'
    OR          tmp_lox_person.fpc_pilot = 'U');

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'FCF Pilot'
    AND         tmp_lox_person.fcf_pilot = 'X';

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'PIT IP'
    AND         tmp_lox_person.pit_ip = 'X';

INSERT INTO pilot_qual
    SELECT      person_line.id, qual.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id 
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        qual
    ON          qual.name = 'SEFE'
    AND         tmp_lox_person.sefe = 'X';

INSERT INTO org (name) VALUES ('M'), ('N'), ('O'), ('P'), ('X');

INSERT INTO pilot_org 
    SELECT      person_line.id, org.id
    FROM        tmp_lox_person
    JOIN        person
    ON          person.tims_id = tmp_lox_person.prsn_id
    JOIN        person_line
    ON          person_line.person_id = person.id
    JOIN        org
    ON          org.name = tmp_lox_person.assigned_org;

CREATE TEMPORARY TABLE tmp_line (
    auth_group_id   INT NOT NULL, 
    num             INT NOT NULL,
    start_date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    org_name        VARCHAR,
    tof_event       VARCHAR,
    fly_go          INT NOT NULL 
);

\COPY tmp_line FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/flying_schedule.csv' delimiter ',' CSV HEADER; 

INSERT INTO shell_line (auth_group_id, num, start_date_time, org_id, fly_go) 
    SELECT auth_group_id, num, start_date_time, org.id, fly_go 
    FROM tmp_line 
    JOIN org 
    ON org.name = SUBSTRING(tmp_line.org_name, POSITION('- ' IN tmp_line.org_name)+2, 1)
    ORDER BY start_date_time, num;

INSERT INTO duty_type (auth_group_id, name) VALUES (1, 'Operations Supervisor'), (1, 'SOF'), (1, 'RSU Controller'), (1, 'RSU Observer');
INSERT INTO duty (auth_group_id, duty_type_id, name) 
VALUES 
    (1, 1, 'OPS SUP 1'), 
    (1, 1, 'OPS SUP 2'), 
    (1, 2, 'SOF 1'), 
    (1, 2, 'SOF 2'), 
    (1, 2, 'SOF 3'),
    (1, 3, 'Tinder 1 CONTROLLER'),
    (1, 3, 'Tinder 2 CONTROLLER'),
    (1, 3, 'Tinder 3 CONTROLLER'),
    (1, 3, 'Tinder 4 CONTROLLER'),
    (1, 4, 'Tinder 1 OBSERVER'),
    (1, 4, 'Tinder 2 OBSERVER'),
    (1, 4, 'Tinder 3 OBSERVER'),
    (1, 4, 'Tinder 4 OBSERVER');

CREATE TEMPORARY TABLE tmp_duty (
    auth_group_id INT,
    duty_asgnmt_id INT,
    duty_id INT,
    duty_catg_cd VARCHAR,
    name_nm VARCHAR,
    trnorg_name_nm VARCHAR,
    asgn_trnorg_name_nm VARCHAR,
    sched_sign_in_date_time_dt TIMESTAMP WITHOUT TIME ZONE,
    sched_sign_out_date_time_dt TIMESTAMP WITHOUT TIME ZONE,
    seq_num_in INT
);

\COPY tmp_duty FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/duty_schedule.csv' delimiter ',' CSV HEADER; 

INSERT INTO shell_duty (auth_group_id, duty_id, start_date_time, end_date_time)
    SELECT tmp_duty.auth_group_id, duty.id, sched_sign_in_date_time_dt, sched_sign_out_date_time_dt
    FROM tmp_duty 
    JOIN duty 
    ON duty.name = tmp_duty.name_nm;

CREATE TEMPORARY TABLE tmp_absence_request (
    status_rqst_id              INT,
    base_rsrc_id                INT,
    prsn_id                     INT,
    last_name_nm                VARCHAR,
    first_name_nm               VARCHAR,
    rsrc_stat_name_nm           VARCHAR,
    rsrc_stat_resn_name_nm      VARCHAR,
    resn_tx                     VARCHAR,
    start_date_time_dt          TIMESTAMP WITHOUT TIME ZONE,
    end_date_time_dt            TIMESTAMP WITHOUT TIME ZONE,
    occur_start_date_time_dt    TIMESTAMP WITHOUT TIME ZONE,
    recur_end_date_time_dt      TIMESTAMP WITHOUT TIME ZONE,
    patt_day_of_week_in         VARCHAR
);

\COPY tmp_absence_request FROM '~/dev/sparkcell-autoscheduler/autoscheduler/res/absence_requests.csv' WITH (delimiter ',', FORMAT csv, HEADER, force_null(occur_start_date_time_dt))

INSERT INTO absence_request (person_id, reason, start_date_time, end_date_time, occur_start_date_time, occur_end_date_time, day_of_week_ptn)
    SELECT 
        person.id,
        tmp_absence_request.resn_tx,
        tmp_absence_request.start_date_time_dt,
        tmp_absence_request.end_date_time_dt,
        tmp_absence_request.occur_start_date_time_dt,
        tmp_absence_request.recur_end_date_time_dt,
        CAST(NULLIF(tmp_absence_request.patt_day_of_week_in, '') AS INT)
    FROM tmp_absence_request 
    JOIN person 
    ON person.id = tmp_absence_request.prsn_id;

INSERT INTO schedule (name, start_date, end_date, submission_date_time, status)
VALUES ('Test_Schedule', '2023-01-02', '2023-01-05', now(), 'Completed');

INSERT INTO schedule (name, start_date, end_date, submission_date_time, status)
VALUES ('Test_Schedule_v2', '2023-01-09', '2023-01-12', now(), 'Completed');

INSERT INTO schedule (name, start_date, end_date, submission_date_time, status)
VALUES ('Test_Schedule_v3', '2023-01-09', '2023-01-12', now(), 'Pending');
CREATE TABLE metadata (
misuse TEXT NOT NULL,
description TEXT NOT NULL,
fix_description TEXT NOT NULL,
violation_types TEXT NOT NULL,
file TEXT NOT NULL,
method TEXT NOT NULL,
diff_url TEXT NOT NULL
);

CREATE TABLE patterns (
misuse TEXT NOT NULL,
name TEXT NOT NULL,
code TEXT NOT NULL,
line TEXT NOT NULL
);

CREATE TABLE stats (
id TEXT NOT NULL,
result TEXT NOT NULL,
runtime TEXT NOT NULL,
number_of_findings TEXT NOT NULL,
exp TEXT NOT NULL,
project TEXT NOT NULL,
version TEXT NOT NULL
);

CREATE TABLE reviews (
exp VARCHAR(100) NOT NULL,
detector VARCHAR(100) NOT NULL,
project VARCHAR(100) NOT NULL,
version VARCHAR(100) NOT NULL,
misuse VARCHAR(100) NOT NULL,
name TEXT NOT NULL,
comment TEXT NOT NULL,
id int AUTO_INCREMENT,
PRIMARY KEY(id)
);

CREATE TABLE review_findings (
decision TEXT NOT NULL,
id int AUTO_INCREMENT,
review int NOT NULL,
PRIMARY KEY(id)
);

CREATE TABLE detectors (
id int AUTO_INCREMENT,
name VARCHAR(100) NOT NULL UNIQUE,
PRIMARY KEY(id)
);

CREATE TABLE types (
id int AUTO_INCREMENT,
name VARCHAR(100) NOT NULL UNIQUE,
PRIMARY KEY(id)
);

CREATE TABLE review_types (
type int NOT NULL,
review int NOT NULL
);

CREATE TABLE finding_types (
finding int NOT NULL,
type int NOT NULL
);

INSERT INTO types (name)
VALUES
    ('missing/call'),
    ('misplaced/call'),
    ('superfluous/call'),
    ('missing/condition/null_check'),
    ('missing/condition/value_or_state'),
    ('missing/condition/synchronization'),
    ('missing/condition/context'),
    ('misplaced/condition/null_check'),
    ('misplaced/condition/value_or_state'),
    ('misplaced/condition/synchronization'),
    ('misplaced/condition/context'),
    ('superfluous/condition/null_check'),
    ('superfluous/condition/value_or_state'),
    ('superfluous/condition/synchronization'),
    ('superfluous/condition/context'),
    ('missing/exception_handling'),
    ('misplaced/exception_handling'),
    ('superfluous/exception_handling'),
    ('missing/iteration'),
    ('misplaced/iteration'),
    ('superfluous/iteration');


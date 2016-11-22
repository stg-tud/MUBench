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
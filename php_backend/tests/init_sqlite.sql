CREATE TABLE IF NOT EXISTS `detectors` (
  `id` INTEGER,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY(`id`)
  );

CREATE TABLE IF NOT EXISTS `stats` (
  `exp` text NOT NULL,
  `detector` text NOT NULL,
  `project` text NOT NULL,
  `version` text NOT NULL,
  `result` text NOT NULL,
  `runtime` text NOT NULL,
  `number_of_findings` text NOT NULL
  );

CREATE TABLE IF NOT EXISTS `metadata` (
  `project` text NOT NULL,
  `version` text NOT NULL,
  `misuse` text NOT NULL,
  `description` text NOT NULL,
  `fix_description` text NOT NULL,
  `violation_types` text NOT NULL,
  `file` text NOT NULL,
  `method` text NOT NULL,
  `diff_url` text NOT NULL
  );

CREATE TABLE IF NOT EXISTS `patterns` (
  `misuse` text NOT NULL,
  `name` text NOT NULL,
  `code` text NOT NULL,
  `line` text NOT NULL
  );

CREATE TABLE IF NOT EXISTS `reviews` (
  `exp` varchar(100) NOT NULL,
  `detector` varchar(100) NOT NULL,
  `project` varchar(100) NOT NULL,
  `version` varchar(100) NOT NULL,
  `misuse` varchar(100) NOT NULL,
  `name` text NOT NULL,
  `comment` text NOT NULL,
  `id` INTEGER NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `meta_snippets` (
  `project` text NOT NULL,
  `version` text NOT NUll,
  `misuse` text NOT NULL,
  `snippet` text NOT NULL,
  `line` INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS `review_findings` (
  `decision` text NOT NULL,
  `id` INTEGER NOT NULL,
  `rank` text NOT NULL,
  `review` INTEGER NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `review_findings_type` (
  `type` INTEGER NOT NULL,
  `review_finding` INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS `finding_snippets` (
  `detector` text NOT NULL,
  `project` text NOT NULL,
  `version` text NOT NUll,
  `finding` text NOT NULL,
  `snippet` text NOT NULL,
  `line` INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS `types` (
  `id` INTEGER NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
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

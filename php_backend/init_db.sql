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
  PRIMARY KEY(`id`)
);

INSERT INTO types (`id`, `name`)
VALUES
    (0, 'missing/call'),
    (1, 'misplaced/call'),
    (2, 'superfluous/call'),
    (3, 'missing/condition/null_check'),
    (4, 'missing/condition/value_or_state'),
    (5, 'missing/condition/synchronization'),
    (6, 'missing/condition/context'),
    (7, 'misplaced/condition/null_check'),
    (8, 'misplaced/condition/value_or_state'),
    (9, 'misplaced/condition/synchronization'),
    (10, 'misplaced/condition/context'),
    (11, 'superfluous/condition/null_check'),
    (12, 'superfluous/condition/value_or_state'),
    (13, 'superfluous/condition/synchronization'),
    (14, 'superfluous/condition/context'),
    (15, 'missing/exception_handling'),
    (16, 'misplaced/exception_handling'),
    (17, 'superfluous/exception_handling'),
    (18, 'missing/iteration'),
    (19, 'misplaced/iteration'),
    (20, 'superfluous/iteration');

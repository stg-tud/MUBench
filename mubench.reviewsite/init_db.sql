
CREATE TABLE IF NOT EXISTS `metadata` (
  `project` varchar(30) NOT NULL,
  `version` varchar(30) NOT NULL,
  `misuse` varchar(30) NOT NULL,
  `description` text NOT NULL,
  `fix_description` text NOT NULL,
  `violation_types` text NOT NULL,
  `file` text NOT NULL,
  `method` text NOT NULL,
  `diff_url` text NOT NULL,
  PRIMARY KEY (`project`,`version`,`misuse`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `meta_snippets` (
  `project` varchar(30) NOT NULL,
  `version` varchar(30) NOT NULL,
  `misuse` varchar(30) NOT NULL,
  `snippet` mediumtext NOT NULL,
  `line` int(11) NOT NULL,
  KEY `lookup` (`project`,`version`,`misuse`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `patterns` (
  `misuse` varchar(30) NOT NULL,
  `name` varchar(30) NOT NULL,
  `code` text NOT NULL,
  `line` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`misuse`,`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `detectors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exp` varchar(10) NOT NULL,
  `detector` varchar(10) NOT NULL,
  `project` varchar(30) NOT NULL,
  `version` varchar(30) NOT NULL,
  `misuse` varchar(30) NOT NULL,
  `name` varchar(30) NOT NULL,
  `comment` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `lookup` (`exp`,`detector`,`project`,`version`,`misuse`,`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `review_findings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `review` int(11) NOT NULL,
  `rank` varchar(10) NOT NULL,
  `decision` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `review` (`review`,`rank`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `review_findings_types` (
  `review_finding` int(11) NOT NULL,
  `type` int(11) NOT NULL,
  PRIMARY KEY (`review_finding`,`type`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `finding_snippets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detector` varchar(10) NOT NULL,
  `project` varchar(30) NOT NULL,
  `version` varchar(30) NOT NULL,
  `finding` varchar(30) NOT NULL,
  `snippet` mediumtext NOT NULL,
  `line` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lookup` (`detector`,`project`,`version`,`finding`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

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

<?php

function get_reviewer_names($dir, $prefix) {
    $prefix .= "_";
    $reviewer_names = array();
    if (is_dir($dir)) {
        foreach (scandir($dir) as $file) {
            if (strpos($file, $prefix) === 0 && substr($file, -4) == ".yml") {
                $reviewer_names[] = basename(substr($file, strlen($prefix)), ".yml");
            }
        }
    }
    return $reviewer_names;
}

function get_reviewer_links($url, $dir, $prefix) {
    $reviewer_names = get_reviewer_names($dir, $prefix);
    foreach ($reviewer_names as $index => $name) {
        $reviewer_names[$index] = "<a href=\"$url?name=$name\">$name</a>";
    }
    return $reviewer_names;
}

function to_review_yml($review) {
    $review_yml = "reviewer: " . $review["name"] . "\n";
    if (!empty($review["comment"])) {
        $review_yml .= "comment: |\n";
        $review_yml .= "  " . str_replace("\n", "\n  ", $review["comment"]) . "\n";
    }
    if (empty($review["findings"])) {
        $review_yml .= "findings: []\n";
    } else {
        $review_yml .= "findings:\n";
        foreach($review["findings"] as $finding_id => $values) {
            $review_yml .= "- id: $finding_id\n";
            $review_yml .= "  assessment: \"" . $values["assessment"] . "\"\n";
            if ($values["violations"]) {
                $review_yml .= "  violations:\n";
                foreach ($values["violations"] as $violation) {
                    $review_yml .= "  - $violation\n";
                }
            }
        }
    }
    return $review_yml;
}

function parse_review_yml($yml) {
    $lines = explode("\n", $yml);
    $line_index = 0;

    $review = array();
    $review["name"] = substr($lines[$line_index], 10);
    $line_index++;

    $review["comment"] = "";
    if (substr($lines[$line_index], 0, 8) == "comment:") {
        $line_index++;
        for (; $line_index < sizeof($lines) && substr($lines[$line_index], 0, 2) == "  "; $line_index++) {
            $review["comment"] .= substr($lines[$line_index], 2);
        }
    }

    $review["findings"] = array();

    if (substr($lines[$line_index], 0, 5) == "hits:") {
        // read old format
        $line_index++; // skip line with "hits:\n" or "hits: []\n"

        $last_id = -1;
        for (; $line_index < sizeof($lines); $line_index++) {
            $line = $lines[$line_index];
            if (substr($line, 0, 5) == "- id:") {
                $last_id = (int) substr($line, 5);
                $review["findings"][$last_id] = array();
                $review["findings"][$last_id]["assessment"] = "Yes";
                $review["findings"][$last_id]["violations"] = array();
            } else if (substr($line, 0, 6) == "  vts:") {
                // skip
            } else if (!empty($line)) {
                $violation = substr($line, 4);
                $review["findings"][$last_id]["violations"][] = $violation;
            }
        }
    } else {
        // read new format
        $line_index++; // skip line with "findings:\n" or "findings: []\n"

        $last_id = -1;
        for (; $line_index < sizeof($lines); $line_index++) {
            $line = $lines[$line_index];
            if (substr($line, 0, 5) == "- id:") {
                $last_id = (int) substr($line, 5);
                $review["findings"][$last_id] = array();
                $review["findings"][$last_id]["violations"] = array();
            } else if (substr($line, 0, 13) == "  assessment:") {
                $assessment = substr($line, 14);
                if (substr($assessment, 0, 1) === "\"") {
                    $assessment = substr($assessment, 1, -1);
                }
                $review["findings"][$last_id]["assessment"] = $assessment;

            } else if (substr($line, 0, 13) == "  violations:") {
                // skip
            } else if (!empty($line)) {
                $violation = substr($line, 4); // strip "  - " prefix
                $review["findings"][$last_id]["violations"][] = $violation;
            }
        }
    }

    return $review;
}

?>

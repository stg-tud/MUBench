<?php

function get_reviewer_names($dir, $prefix) {
    $reviewer_names = array();
    if (is_dir($dir)) {
        foreach (scandir($dir) as $file) {
            if (strpos($file, $prefix) === 0 && substr($file, -4) == ".yml") {
                $reviewer_names[] = basename(substr($file, strlen($prefix) + 1), ".yml");
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

function to_review_yml($name, $comment, $finding_ids, $findings_vtypes) {
    $review = "reviewer: $name\n";
    if (!empty($comment)) {
        $review .= "comment: |\n";
        $review .= "  " . str_replace("\n", "\n  ", $comment) . "\n";
    }
    if (empty($finding_ids)) {
        $review .= "hits: []\n";
    } else {
        $review .= "hits:\n";
        foreach($finding_ids as $finding_id) {
            $review .= "- id: $finding_id\n";
            if (!empty($findings_vtypes[$finding_id])) {
                $review .= "  vts:\n";
                foreach ($findings_vtypes[$finding_id] as $finding_vtype) {
                    $review .= "  - $finding_vtype\n";
                }
            }
        }
    }
    return $review;
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

    $line_index++; // skip line with "hits:\n" or "hits: []\n"
    $review["hits"] = array();

    $last_id = -1;
    for (; $line_index < sizeof($lines); $line_index++) {
        $line = $lines[$line_index];
        if (substr($line, 0, 5) == "- id:") {
            $last_id = (int) substr($line, 5);
            $review["hits"][$last_id] = array();
            $line_index++; // skip line with "  vts:\n"
        } else if (!empty($line)) {
            $violation_type = substr($line, 4);
            $review["hits"][$last_id][] = $violation_type;
        }
    }

    return $review;
}

?>

<?php

function get_reviewer_names($dir, $prefix) {
    $reviewer_names = array();
    foreach (scandir($dir) as $file) {
        if (strpos($file, $prefix) === 0 && substr($file, -4) == ".yml") {
            $reviewer_names[] = basename(substr($file, strlen($prefix) + 1), ".yml");
        }
    }
    return $reviewer_names;
}

?>
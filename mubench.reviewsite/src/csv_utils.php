<?php

function createCSV($rows)
{
    $lines = [];
    $header = [];
    foreach ($rows as $line) {
        $lines[] = implode(',', $line);

        $columns = array_keys($line);
        if(count($columns) > count($header)){
            $header = $columns;
        }
    }
    array_unshift($lines, implode(',', $header));
    array_unshift($lines, "sep=,");
    return implode("\n", $lines);
}

function escapeText($text){
    return "\"" . $text . "\"";
}

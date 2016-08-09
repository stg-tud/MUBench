<?php
////////////////////////////////////////////////////////////////////////////////////////////////
// input sanitization

$name = str_replace(" ", "_", trim($_POST["reviewer_name"]));
if (empty($name)) die("<span style=\"color:red\">Review not saved! Please specify your name...</span>");


$review_name = $_POST["review_name"];
if (empty($review_name)) {
    $review_name = array();
}
$review_name = join("/", array_map("sanitize_path_name", $review_name)) . "_$name.yml";
function sanitize_path_name($name) {
    return str_replace(array("/", "\\", ".."), "_", $name);
}


$finding_ids = $_POST["finding_ids"];
if (empty($finding_ids)) {
    echo "<span style=\"color:red\">You did not select any hits. Are you sure?</span><br>";
} else {
    if(($key = array_search(-1, $finding_ids)) !== false) {
        unset($finding_ids[$key]);
    }

    if (array_key_exists("violation_types", $_POST)) {
        $findings_vtypes = $_POST["violation_types"];
    } else {
        $findings_vtypes = array();
    }

    foreach ($finding_ids as $finding_id) {
        if (!array_key_exists($finding_id, $findings_vtypes)) {
            $findings_vtypes[$finding_id] = array();
        }
    }
}


$comment = str_replace("\r", "", $_POST["reviewer_comment"]);

////////////////////////////////////////////////////////////////////////////////////////////////
// generate review yml

include_once "review_utils.php";
$review_yml = to_review_yml($name, $comment, $finding_ids, $findings_vtypes);
$review_file = fopen($review_name, "w") or die("<span style=\"color:red\">Failed to write review file!</span>");
fwrite($review_file, mb_convert_encoding($review, 'UTF-8', 'auto'));
fclose($review_file);
echo "<span style=\"color:green\">Review successfully saved.</span>";

?>

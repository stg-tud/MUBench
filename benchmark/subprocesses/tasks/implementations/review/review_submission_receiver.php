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


$finding_ids = $_POST["finding_ids"] or array();
if($finding_ids && ($key = in_array(-1, $finding_ids)) !== false) {
    unset($finding_ids[$key]);
}
if (!$finding_ids) {
    echo "<span style=\"color:red\">You did not select any hits. Are you sure?</span><br>";
} else {
    $hits = $_POST["violation_types"] or array();

    foreach ($finding_ids as $finding_id) {
        if (!$hits[$finding_id]) {
            $hits[$finding_id] = array();
        }
    }
}


$comment = str_replace("\r", "", $_POST["reviewer_comment"]);

////////////////////////////////////////////////////////////////////////////////////////////////
// generate review yml

include_once "review_utils.php";
$review_yml = to_review_yml($name, $comment, $hits);
$review_file = fopen($review_name, "w") or die("<span style=\"color:red\">Failed to write review file!</span>");
fwrite($review_file, mb_convert_encoding($review_yml, 'UTF-8', 'auto'));
fclose($review_file);
echo "<span style=\"color:green\">Review successfully saved.</span>";

?>

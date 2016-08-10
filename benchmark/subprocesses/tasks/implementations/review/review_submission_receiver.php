<?php
////////////////////////////////////////////////////////////////////////////////////////////////
// input sanitization

$review = array();

$review["name"] = str_replace(" ", "_", trim($_POST["reviewer_name"]));
if (empty($review["name"])) die("<span style=\"color:red\">Review not saved! Please specify your name...</span>");


$review_file_name = $_POST["review_name"];
if (empty($review_name)) {
    $review_name = array();
}
$review_file_name = join("/", array_map("sanitize_path_name", $review_file_name)) . "_" . $review["name"] . ".yml";
function sanitize_path_name($name) {
    return str_replace(array("/", "\\", ".."), "_", $name);
}


$review["findings"] = $_POST["findings"] or array();
if (!$review["findings"]) {
    echo "<span style=\"color:red\">You did not select any findings. Are you sure?</span><br>";
}


$review["comment"] = str_replace("\r", "", $_POST["reviewer_comment"]);

////////////////////////////////////////////////////////////////////////////////////////////////
// generate review yml

include_once "review_utils.php";
$review_yml = to_review_yml($review);
$review_file = fopen($review_file_name, "w") or die("<span style=\"color:red\">Failed to write review file!</span>");
fwrite($review_file, mb_convert_encoding($review_yml, 'UTF-8', 'auto'));
fclose($review_file);
echo "<span style=\"color:green\">Review successfully saved.</span>";

?>

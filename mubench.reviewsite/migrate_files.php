<?php

set_time_limit(0);

require __DIR__ . '/vendor/autoload.php';
$settings = require __DIR__ . '/settings.php';
$new_db = $settings["db"];

$capsule = new \Illuminate\Database\Capsule\Manager;
$capsule->addConnection($new_db);
$capsule->setAsGlobal();
$capsule->bootEloquent();

// The schema accesses the database through the app, which we do not have in
// this context. Therefore, use an array to provide the database. This seems
// to work fine.
/** @noinspection PhpParamsInspection */
\Illuminate\Support\Facades\Schema::setFacadeApplication(["db" => $capsule]);
$detectors = \MuBench\ReviewSite\Models\Detector::all();
$experiments = \MuBench\ReviewSite\Models\Experiment::all();

$old_upload_path = $settings['upload'];
$new_upload_path = $settings['upload'];

foreach($experiments as $experiment){
    foreach($detectors as $detector){
        $runs = \MuBench\ReviewSite\Models\Run::of($detector)->in($experiment)->get();
        foreach($runs as $run){
            $old_dir = $old_upload_path . "/ex$experiment->id/$detector->muid/$run->project_muid/$run->version_muid";
            if(is_dir($old_dir)){
                $new_dir = $new_upload_path . "/$experiment->id/$detector->id/$run->project_muid/$run->version_muid";
                mkdir($new_dir, 0745, true);
                $files = glob("$old_dir/*.*");
                foreach($files as $file){
                    $file_to_go = str_replace($old_dir,$new_dir,$file);
                    copy($file, $file_to_go);
                }
            }
        }
    }
}

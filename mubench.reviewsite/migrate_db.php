<?php

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Events\Dispatcher;
use Illuminate\Support\Facades\Schema;
use MuBench\ReviewSite\Controllers\RunsController;
use MuBench\ReviewSite\Models\Detector;
use MuBench\ReviewSite\Models\Experiment;
use MuBench\ReviewSite\Models\Metadata;
use MuBench\ReviewSite\Models\Type;
use Illuminate\Container\Container;

session_start();
date_default_timezone_set('Europe/Berlin');
set_time_limit(0);

require __DIR__ . '/vendor/autoload.php';

$settings = require __DIR__ . '/settings.php';
$app = new \Slim\App($settings);

$container = $app->getContainer();

$old_db = [
    'driver' => 'mysql',
    'host' => 'localhost:8889',
    'database' => 'mubench_old',
    'username' => 'root',
    'password' => 'root',
    'charset'   => 'utf8',
    'collation' => 'utf8_unicode_ci',
    'prefix'    => 'mubench_icse18_',
];
$new_db = $settings['db'];

$capsule = new \Illuminate\Database\Capsule\Manager;
$capsule->addConnection($new_db);
$capsule->addConnection($old_db, 'old_db');
$capsule->setAsGlobal();
$capsule->setEventDispatcher(new Dispatcher(new Container()));
$capsule->bootEloquent();

// The schema accesses the database through the app, which we do not have in
// this context. Therefore, use an array to provide the database. This seems
// to work fine.
/** @noinspection PhpParamsInspection */
\Illuminate\Support\Facades\Schema::setFacadeApplication(["db" => $capsule]);

require __DIR__ . '/setup/create_database_tables.php';

echo '<h2>Migrating DB</h2><br/>';

echo 'Migrating types...<br/>';
$types = MuBench\ReviewSite\Old\Type::all();
foreach($types as $type){
    MuBench\ReviewSite\Models\Type::create(['name' => $type->name]);
}

echo 'Migrating metadata...<br/>';
$metadata = \MuBench\ReviewSite\Old\Metadata::all();
foreach($metadata as $old_metadata){
    $misuseId = $old_metadata->misuse;
    $projectId = $old_metadata->project;
    $versionId = $old_metadata->version;
    $new_metadata =\MuBench\ReviewSite\Models\Metadata::firstOrNew(['project_muid' => $projectId, 'version_muid' => $versionId, 'misuse_muid' => getShortId($misuseId, $projectId)]);
    $new_metadata->description = $old_metadata->description;
    $new_metadata->fix_description = $old_metadata->fix_description;
    $new_metadata->diff_url = $old_metadata->diff_url;
    $new_metadata->file = $old_metadata->file;
    $new_metadata->method = $old_metadata->method;
    $new_metadata->save();
    $patterns = \MuBench\ReviewSite\Old\Pattern::where('misuse', $misuseId)->get();
    savePatterns($new_metadata->id, $patterns);
    $metadata_snippets = \MuBench\ReviewSite\Old\MetadataSnippet::where('project', $projectId)
        ->where('version', $versionId)
        ->where('misuse', $misuseId)->get();
    saveSnippets($projectId, $versionId, $new_metadata->misuse_muid, $new_metadata->file, $metadata_snippets);
    if($old_metadata->violation_types){
        saveViolationTypes($new_metadata->id, explode(';', $old_metadata->violation_types));
    }else{
        $types = $capsule->getConnection('old_db')->table('misuse_types')->where(['project' => $projectId, 'version' => $versionId, 'misuse' => $misuseId])->get();
        if($types && sizeof($types) > 0){
            foreach($types as $type){
                $new_metadata->violation_types()->attach($type->type);
            }
        }
    }

}
$detectors = \MuBench\ReviewSite\Old\Detector::all();
$runsController = new RunsController($container);
echo 'Migrating detectors...<br/>';
try {
    foreach ($detectors as $index => $old_detector) {
        echo "Migrating everything for " . $old_detector->name . " - " . ($index + 1) . "/" . sizeof($detectors) . "...<br/>";
        $new_detector = $runsController->createDetector($old_detector->name);
        $runs = MuBench\ReviewSite\Old\Run::of($old_detector)->get();
        foreach ($runs as $index => $run) {
            createOrUpdateRunTable($new_detector, $run);
            if ($run['exp'] === 'ex1') {
                $experiment = $experiment1;
            } else if ($run['exp'] === 'ex2') {
                $experiment = $experiment2;
            } else {
                $experiment = $experiment3;
            }
            $new_run = new \MuBench\ReviewSite\Models\Run;
            $new_run->setDetector($new_detector);
            $new_run = $capsule->table($new_run->getTable())->where(['experiment_id' => $experiment->id,
                'project_muid' => $run['project'], 'version_muid' => $run['version']])->first();
            if (!$new_run) {
                $new_run = new \MuBench\ReviewSite\Models\Run;
                $new_run->setDetector($new_detector);
                foreach ($run->getAttributes() as $key => $value) {
                    if ($key === 'exp') {
                        $new_run->experiment_id = $experiment->id;
                    } else if ($key === 'project') {
                        $new_run->project_muid = $value;
                    } else if ($key === 'version') {
                        $new_run->version_muid = $value;
                    } else {
                        $new_run[$key] = $value;
                    }
                }
                $new_run->save();
            }

            $findings = MuBench\ReviewSite\Old\Finding::of($old_detector)
                ->where('exp', $run->exp)
                ->where('project', $run->project)
                ->where('version', $run->version)->get();
            // echo 'Migrating ' . $index . '. run with ' . sizeof($findings) . ' findings<br/>';
            if ($experiment->id === 1 || $experiment->id === 3) {
                $metadata = \MuBench\ReviewSite\Models\Metadata::where(['project_muid' => $run->project, 'version_muid' => $run->version])->get();
                foreach ($metadata as $data) {
                    if (sizeof($data->patterns) === 0 && $experiment->id === 1) {
                        continue;
                    }
                    \MuBench\ReviewSite\Models\Misuse::firstOrCreate(['metadata_id' => $data->id, 'misuse_muid' => $data->misuse_muid, 'run_id' => $new_run->id, 'detector_id' => $new_detector->id]);
                }
            }
            foreach ($findings as $finding) {
                $projectId = $finding['project'];
                $versionId = $finding['version'];
                $misuseId = $finding['misuse'];
                createOrUpdateFindingsTable($new_detector, $finding);
                $new_misuse = getOrCreateMisuse($new_detector, $experiment, $projectId, $versionId, $misuseId, $new_run->id);
                $new_finding = new \MuBench\ReviewSite\Models\Finding;
                $new_finding->setDetector($new_detector);
                $new_finding->misuse_id = $new_misuse->id;
                foreach ($finding->getAttributes() as $key => $value) {
                    if ($key === 'exp') {
                        $new_finding->experiment_id = $experiment->id;
                    } else if ($key === 'project') {
                        $new_finding->project_muid = $value;
                    } else if ($key === 'version') {
                        $new_finding->version_muid = $value;
                    } else if ($key === 'misuse') {
                        $new_finding->misuse_muid = getShortId($value, $finding->getAttributes()['project']);
                    } else {
                        $new_finding[$key] = $value;
                    }
                }
                $new_finding->save();
                $findingSnippets = \MuBench\ReviewSite\Old\FindingSnippet::where('project', $projectId)
                    ->where('version', $versionId)
                    ->where('finding', $misuseId)
                    ->where('detector', $old_detector->id)->get();
                saveSnippets($projectId, $versionId, $new_finding->misuse_muid, $new_finding->file, $findingSnippets);
                $reviews = \MuBench\ReviewSite\Old\Review::where('exp', $run['exp'])
                    ->where('detector', $old_detector->id)
                    ->where('project', $projectId)
                    ->where('version', $versionId)
                    ->where('misuse', $misuseId)->get();
                foreach ($reviews as $review) {
                    createReview($new_misuse->id, $review);
                }
            }
        }
    }
} catch (Exception $e) {
    echo '<br/>';
    echo '<b>' . $e->getMessage() . '</b>';
    echo nl2br($e->getTraceAsString());
}

function addColumns($old_obj, $new_obj, $ignore_columns)
{
    $existing_columns = Schema::getColumnListing($new_obj->getTable());
    $columns = Schema::connection('old_db')->getColumnListing($old_obj->getTable());
    $columns = array_diff($columns, $ignore_columns);
    $columns = array_diff($columns, $existing_columns);
    foreach($columns as $column){
        Schema::table($new_obj->getTable(), function ($table) use ($column) {
            $table->text($column)->nullable();
        });
    }
}

function getOrCreateMisuse(Detector $detector, Experiment $experiment, $projectId, $versionId, $misuseId, $runId)
{
    $misuseId = getShortId($misuseId, $projectId);
    if ($experiment->id === 1 || $experiment->id === 3) {
        $new_metadata = getOrCreateMetadata($projectId, $versionId, $misuseId);
        if($new_metadata){
            $misuse = \MuBench\ReviewSite\Models\Misuse::firstOrCreate(['metadata_id' => $new_metadata->id, 'misuse_muid' => $misuseId, 'run_id' => $runId, 'detector_id' => $detector->id]);
        }
    } else {
        $misuse = \MuBench\ReviewSite\Models\Misuse::firstOrCreate(['misuse_muid' => $misuseId, 'run_id' => $runId, 'detector_id' => $detector->id]);
    }
    return $misuse;
}

function getOrCreateMetadata($projectId, $versionId, $misuseId)
{
    $new_metadata =\MuBench\ReviewSite\Models\Metadata::firstOrCreate(['project_muid' => $projectId, 'version_muid' => $versionId, 'misuse_muid' => $misuseId]);
    return $new_metadata;
}

function saveViolationTypes($metadataId, $violationTypes)
{
    foreach ($violationTypes as $type_name) {
        $violation_type = Type::firstOrCreate(['name' => $type_name]);
        Metadata::find($metadataId)->violation_types()->attach($violation_type);
    }
}

function savePatterns($metadataId, $patterns)
{
    if ($patterns) {
        foreach ($patterns as $pattern) {
            $p = \MuBench\ReviewSite\Models\Pattern::firstOrNew(['metadata_id' => $metadataId]);
            $p->code = $pattern->code;
            $p->line = $pattern->line;
            $p->save();
        }
    }
}

function saveSnippets($projectId, $versionId, $misuseId, $file, $snippets)
{
    if ($snippets) {
        foreach ($snippets as $snippet) {
            \MuBench\ReviewSite\Controllers\SnippetsController::createSnippetIfNotExists($projectId, $versionId, $misuseId, $file, $snippet->line, $snippet->snippet);
        }
    }
}

function createReview($misuse_id, $old_review)
{
    global $capsule;
    $reviewer = \MuBench\ReviewSite\Models\Reviewer::firstOrCreate(['name' => $old_review->name]);
    $review = \MuBench\ReviewSite\Models\Review::firstOrNew(['misuse_id' => $misuse_id, 'reviewer_id' => $reviewer->id]);
    $review->comment = $old_review->comment;
    $review->save();

    foreach ($old_review->finding_reviews as $old_findingReview) {
        $new_findingReview = \MuBench\ReviewSite\Models\FindingReview::firstOrNew(['review_id' => $review->id, 'rank' => intval($old_findingReview->rank)]);
        $new_findingReview->decision = $old_findingReview->decision;
        $new_findingReview->save();
        if (sizeof($old_findingReview->review_types) > 0) {
            foreach ($old_findingReview->review_types as $type) {
                $new_findingReview->violation_types()->attach($type->type);
            }
        }
    }
}

function createOrUpdateRunTable($detector, $old_run)
{
    $run = new \MuBench\ReviewSite\Models\Run;
    $run->setDetector($detector);
    if (!Schema::hasTable($run->getTable())) {
        Schema::create($run->getTable(), function (Blueprint $table) {
            $table->increments('id');
            $table->integer('experiment_id');
            $table->string('project_muid', 30);
            $table->string('version_muid', 30);
            $table->float('runtime');
            $table->integer('number_of_findings')->nullable();
            $table->string('result', 30);
            $table->dateTime('created_at');
            $table->dateTime('updated_at');
        });
    }
    addColumns($old_run, $run, ['exp', 'version', 'project']);
}

function createOrUpdateFindingsTable($detector, $old_finding)
{
    $finding = new \MuBench\ReviewSite\Models\Finding;
    $finding->setDetector($detector);
    if(!Schema::hasTable($finding->getTable())){
        Schema::create($finding->getTable(), function (Blueprint $table) {
            $table->increments('id');
            $table->integer('experiment_id');
            $table->integer('misuse_id');
            $table->string('project_muid', 30);
            $table->string('version_muid', 30);
            $table->string('misuse_muid', 30);
            $table->integer('startline');
            $table->integer('rank');
            $table->text('file');
            $table->text('method');
            $table->dateTime('created_at');
            $table->dateTime('updated_at');
        });
    }
    addColumns($old_finding, $finding, ['exp', 'version', 'project', 'misuse']);
}

function getShortId($misuseId, $projectId)
{
    return substr($misuseId, 0, strlen($projectId)) === $projectId ? substr($misuseId, strlen($projectId) + 1) :
        $misuseId;
}


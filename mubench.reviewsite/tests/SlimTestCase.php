<?php

use Illuminate\Container\Container;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Events\Dispatcher;
use Illuminate\Support\Facades\Schema;
use PHPUnit\Framework\TestCase;
use Monolog\Logger;
use Pixie\QueryBuilder\QueryBuilderHandler;
use Slim\Http\Environment;
use Slim\Http\Headers;
use Slim\Http\Request;
use Slim\Http\RequestBody;
use Slim\Http\Response;
use Slim\Http\Uri;

class SlimTestCase extends TestCase
{
    protected $app;

    /** @var Request */
    protected $request;

    /** @var Response */
    protected $response;

    /**
     * @var Logger $logger
     */
    protected $logger;

    /** @var \Illuminate\Database\Capsule\Manager */
    protected $db;

    /** @var  \Illuminate\Support\Facades\Schema */
    protected $schema;

    public function setUp(){
        $settings = [
            'displayErrorDetails' => true, // set to false in production
            'addContentLengthHeader' => false, // Allow the web server to send the content-length header

            'db' => [
                'driver' => 'sqlite',
                'host' => 'localhost',
                'database' => ':memory:',
                'username' => 'admin',
                'password' => 'admin',
                'charset'   => 'utf8',
                'collation' => 'utf8_unicode_ci',
                'prefix'    => '',
            ],

            // Monolog settings
            'logger' => [
                'name' => 'mubench',
                'path' => __DIR__ . '/../logs/app.log',
                'level' => \Monolog\Logger::DEBUG,
            ],
            'site_base_url' => '/',
            'upload' => "./upload",
            'users' => [
                "admin" => "pass"
            ],
            'default_ex2_review_size' => '20'
        ];
        $app = new \Slim\App($settings);
        require __DIR__ . '/../bootstrap/bootstrap.php';
        $this->logger = new \Monolog\Logger("test");

        require __DIR__ . '/../setup/create_database_tables.php';
        require __DIR__ . '/../src/routes.php';
        require_once __DIR__ . '/../src/route_utils.php';
        require_once __DIR__ . '/../src/csv_utils.php';
        \MuBench\ReviewSite\Models\Detector::flushEventListeners();
        \MuBench\ReviewSite\Models\Detector::boot();
        $this->app = $app;
        $this->container = $app->getContainer();
    }

    public function get($path, $data = array(), $optionalHeaders = array()){
        return $this->request('get', $path, $data, $optionalHeaders);
    }

    private function request($method, $path, $data = array(), $optionalHeaders = array()){
        //Make method uppercase
        $method = strtoupper($method);
        $options = array(
            'REQUEST_METHOD' => $method,
            'REQUEST_URI'    => $path
        );
        if ($method === 'GET') {
            $options['QUERY_STRING'] = http_build_query($data);
        } else {
            $params  = json_encode($data);
        }
        // Prepare a mock environment
        $env = Environment::mock(array_merge($options, $optionalHeaders));
        $uri = Uri::createFromEnvironment($env);
        $headers = Headers::createFromEnvironment($env);
        $serverParams = $env->all();
        $body = new RequestBody();
        // Attach JSON request
        if (isset($params)) {
            $headers->set('Content-Type', 'application/json;charset=utf8');
            $body->write($params);
        }
        $this->request  = new Request($method, $uri, $headers, array(), $serverParams, $body);
        $response = new Response();
        // Invoke request
        $app = $this->app;
        $this->response = $app($this->request, $response);
        // Return the application output.
        return $this->response->getBody();
    }

    private function mySQLToSQLite($mysql){
        $lines = explode("\n", $mysql);
        for ($i = count($lines) - 1; $i >= 0; $i--) {
            // remove all named keys, i.e., leave only PRIMARY keys
            if (strpos($lines[$i], 'KEY `') !== false) {
                $lines[$i] = "";
                $lines[$i - 1] = substr($lines[$i - 1], 0, -1); // remove trailing comma in previous line
            }
        }
        $sqlite = implode("\n", $lines);
        $sqlite = str_replace("AUTO_INCREMENT", "", $sqlite);
        $sqlite = str_replace("int(11)", "INTEGER", $sqlite);
        $sqlite = str_replace(" ENGINE=MyISAM  DEFAULT CHARSET=latin1;", ";", $sqlite);
        return $sqlite;
    }

    protected function createFindingWith($experiment, $detector, $misuse)
    {
        $finding = new \MuBench\ReviewSite\Models\Finding;
        $finding->setDetector($detector);
        Schema::dropIfExists($finding->getTable());
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
                $table->integer('additional_column')->nullable();
                $table->text('file');
                $table->text('method');
                $table->dateTime('created_at');
                $table->dateTime('updated_at');
            });
        }

        $finding->experiment_id = $experiment->id;
        $finding->misuse_id = $misuse->id;
        $finding->project_muid = 'mubench';
        $finding->version_muid = '42';
        $finding->misuse_muid = '0';
        $finding->startline = 113;
        $finding->rank = 1;
        $finding->file = 'Test.java';
        $finding->method = "method(A)";
        $finding->save();
    }
}
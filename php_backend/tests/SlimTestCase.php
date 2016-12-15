<?php
require_once __DIR__ . '/../vendor/autoload.php';
require_once __DIR__ . '/../src/ConnectionDB.php';
require_once __DIR__ . '/../src/DirectoryHelper.php';
require_once __DIR__ . '/../src/UploadProcessor.php';
require_once __DIR__ . '/../src/DataProcessor.php';
require_once __DIR__ . '/../src/RoutesHelper.php';

use Slim\Http\Environment;
use Slim\Http\Headers;
use Slim\Http\Request;
use Slim\Http\RequestBody;
use Slim\Http\Response;
use Slim\Http\Uri;

class SlimTestCase extends PHPUnit_Framework_TestCase
{

    protected $app;

    public function setUp(){
        // Run app
        $this->app = $this->getSlimInstance();
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

    public function getSlimInstance(){
        // Prepare a mock environment
        // Instantiate the app
        $settings = require __DIR__ . '/../src/settings.php';
        $app = new \Slim\App($settings);

        // Set up dependencies
        require __DIR__ . '/../src/dependencies.php';

        $pdo = new PDO('sqlite::memory:');
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        $logger = $app->getContainer()['logger'];
        $db = new DBConnection($pdo, $logger);
        $app->upload = new UploadProcessor($db, $logger);
        $app->dir = new DirectoryHelper($settings['upload'], $logger);
        $app->data = new DataProcessor($db, $logger);
        $app->helper = new RoutesHelper($logger);
        // Routes
        require __DIR__ . '/../src/routes.php';

        return $app;
    }
}
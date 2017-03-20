<?php
return [
    'settings' => [
        'displayErrorDetails' => true, // set to false in production
        'addContentLengthHeader' => false, // Allow the web server to send the content-length header

        // Renderer settings
        'renderer' => [
            'template_path' => __DIR__ . '/../templates/',
        ],

        // Monolog settings
        'logger' => [
            'name' => 'mubench',
            'path' => __DIR__ . '/../logs/app.log',
            'level' => \Monolog\Logger::DEBUG,
        ],
    ],
    'ex_template' => [
        "ex1" => [
        "title" => "Detect Only",
        "id" => "1"
        ],
        "ex2" => [
        "title" => "All Findings",
        "id" => "2"
        ],
        "ex3" => [
        "title" => "Benchmark",
        "id" => "3"
        ]
    ],
    'db' => [
        'driver'    => 'mysql',
        'host'      => 'localhost',
        'database'  => 'database',
        'username'  => 'username',
        'password'  => 'password',
        'charset'   => 'utf8',
        'collation' => 'utf8_unicode_ci',
        'prefix'    => 'mubench_',
        'options'   => array(
            PDO::MYSQL_ATTR_USE_BUFFERED_QUERY => true,
        )
    ],
    'upload' => "./upload",
    'users' => [
        "admin" => "pass",
        "admin2" => "pass"
    ],
    'root_url' => '/'
];

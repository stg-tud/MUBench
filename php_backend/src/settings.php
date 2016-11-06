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
        "title" => "All Findings (Top 10 per Project)",
        "id" => "2"
        ],
        "ex3" => [
        "title" => "Mine and Detect",
        "id" => "3"
        ]
    ],
    'db' => [
        'user' => 'root',
        'password' => 'mubench',
        'url' => 'localhost',
        'name' => 'mubench'
    ]
];

<?php


namespace MuBench\ReviewSite;

class LoggingError {
    private $logger;
    private $displayErrorDetails;

    function __construct(\Monolog\Logger $logger, $displayErrorDetails)
    {
        $this->logger = $logger;
        $this->displayErrorDetails = $displayErrorDetails;
    }

    /**
     * @param \Slim\Http\Request $request
     * @param \Slim\Http\Response $response
     * @param \Exception $exception
     * @return \Slim\Http\Response
     */
    public function __invoke($request, $response, $exception) {
        $this->logger->critical($exception);

        if ($this->displayErrorDetails) {
            $message = $exception->getMessage();
        } else {
            $message = "Ops! Something went wrong.";
        }

        return $response->withStatus(500)
            ->withHeader('Content-Type', 'text/html')
            ->write($message);
    }
}

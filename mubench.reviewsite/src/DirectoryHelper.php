<?php

namespace MuBench\ReviewSite;

use Monolog\Logger;
use RecursiveDirectoryIterator;
use RecursiveIteratorIterator;

class DirectoryHelper {

	private $root;

    /**
     * @var Logger $logger
     */
	private $logger;

	function __construct($root, $logger){
		$this->root = $root;
		$this->logger = $logger;
	}

	public function deleteOldImages($ex, $detector, $project, $version){
        $path = $this->buildPath($ex, $detector, $project, $version);
        if(file_exists($path)){
            $it = new RecursiveDirectoryIterator($path, RecursiveDirectoryIterator::SKIP_DOTS);
            $files = new RecursiveIteratorIterator($it, RecursiveIteratorIterator::CHILD_FIRST);
            foreach($files as $file) {
                if ($file->isDir()){
                    rmdir($file->getRealPath());
                } else {
                    unlink($file->getRealPath());
                }
            }
            rmdir($path);
        }
    }

	public function handleImage($ex, $detector, $project, $version, $img){
        $path = $this->buildPath($ex, $detector, $project, $version);
		$file = $path . $img->getClientFilename();
		$this->logger->info("moving file " . $img->getClientFilename() . " to " . $path);
        if(file_exists($file)) {
            unlink($file);
        }
        mkdir($path, 0745, true);
		$img->moveTo($file);
	}

	private function buildPath($ex, $detector, $project, $version){
	    return $this->root . "/" . $ex .  "/" . $detector . "/" . $project . "/" . $version . "/";
    }

}
<?php

class DirectoryHelper {

	private $root;
	private $logger;

	function __construct($root, $logger){
		$this->root = $root;
		$this->logger = $logger;
	}

	public function deleteOldImages($ex, $dataset, $detector, $project, $version){
        $path = $this->buildPath($ex, $dataset, $detector, $project, $version);
        if(file_exists($path)){
            $it = new RecursiveDirectoryIterator($path, RecursiveDirectoryIterator::SKIP_DOTS);
            $files = new RecursiveIteratorIterator($it,
                RecursiveIteratorIterator::CHILD_FIRST);
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

	public function handleImage($ex, $dataset, $detector, $project, $version, $img){
        $path = $this->buildPath($ex, $dataset, $detector, $project, $version);
		$file = $path . $img->getClientFilename();
		$this->logger->info("moving file " . $img->getClientFilename() . " to " . $path);
        mkdir($path, 0745, true);
		$img->moveTo($file);
	}

	private function buildPath($ex, $dataset, $detector, $project, $version){
	    return $this->root . "/" . $ex . "/" . $dataset . "/" . $detector . "/" . $project . "/" . $version . "/";
    }

}
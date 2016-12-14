<?php

class DirectoryHelper {

	private $root;
	private $logger;

	function __construct($root, $logger){
		$this->root = $root;
		$this->logger = $logger;
	}

	public function deleteOldImages($ex, $project, $version){
        $path = $this->root . "/" . $ex . "/" . $project . "/" . $version . "/";
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

	public function handleImage($ex, $project, $version, $img){
        $path = $this->root . "/" . $ex . "/" . $project . "/" . $version . "/";
		$file = $path . $img->getClientFilename();
		$this->logger->info('Moved img: ' . $img->getClientFilename() . " to " . mkdir($path, 0745, true));
		$img->moveTo($file);
	}

}
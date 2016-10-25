<?php

class DirectoryHelper {

	private $root;
	private $logger;

	function __construct($root, $logger){
		$this->root = $root;
		$this->logger = $logger;
	}

	public function handleImage($prefix, $project, $version, $img){
		$path = $this->root . "/" . $prefix . "/" . $project . "/" . $version;
		if(file_exists($path)){
			$this->deleteDir($path);
		}
		mdkir($path, 0777, true);
		$img->moveTo($path . $img->getClientFilename());
	}

	public function deleteDir($dirPath) {
	    if (! is_dir($dirPath)) {
	        throw new InvalidArgumentException("$dirPath must be a directory");
	    }
	    if (substr($dirPath, strlen($dirPath) - 1, 1) != '/') {
	        $dirPath .= '/';
	    }
	    $files = glob($dirPath . '*', GLOB_MARK);
	    foreach ($files as $file) {
	        if (is_dir($file)) {
	            $this->deleteDir($file);
	        } else {
	            unlink($file);
	        }
	    }
	    rmdir($dirPath);
	}
}
<?php

class DirectoryHelper {

	private $root;
	private $logger;

	function __construct($root, $logger){
		$this->root = $root;
		$this->logger = $logger;
	}

	public function handleImage($ex, $project, $version, $img){
		$path = $this->root . "/" . $project . "/" . $version . "/";
		$file = $path . $img->getClientFilename();
		if(file_exists($file)){
			unlink($file);
		}
		$this->logger->info(mkdir($path, 0700, true));
		$img->moveTo($file);
	}

}
<?php

class DirectoryHelper {

	private $root;
	private $logger;

	function __construct($root, $logger){
		$this->root = $root;
		$this->logger = $logger;
	}

	public function handleImage($ex, $id, $img){
		$this->logger->info("FOO");
		$path = $this->root . "/" . $id . "/";
		$this->logger->info($mg);
		$file = $path . $img->getClientFilename();
		$this->logger->info($path);
		if(file_exists($file)){
			unlink($file);
		}
		$this->logger->info(mkdir($path, 0700, true));
		$img->moveTo($file);
	}

}
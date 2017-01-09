<?php

use Monolog\Logger;

class DataProcessor {

	private $db;
	private $logger;

	function __construct(DBConnection $db, Logger $logger){
		$this->db = $db;
		$this->logger = $logger;
	}

	public function getMetadata($misuse){
		$query = $this->db->getMetadata($misuse);
		foreach($query as $q){
			$data = $q;
			$data['violation_types'] = explode(";", $q['violation_types']);
			return $data;
		}
	}

	public function getReview($exp, $set, $detector, $project, $version, $misuse, $reviewer){
		$query = $this->db->getReview($reviewer, $exp . "_" . $set . "_" . $detector . "_" . $project . "_" . $version . "_" . $misuse);
		$result = [];
		foreach($query as $q){
			$q['types'] = explode(";", $q['violation_type']);
			$result[$q['id']] = $q;
		}
		return $result;
	}

	public function getPatterns($misuse){
		$query = $this->db->getPattern($misuse);
		foreach($query as $q){
			return $q;
		}
	}

	public function getHits($table, $project, $version, $misuse, $exp){
		$query = $this->db->getHits($table, $project, $version, $misuse, $exp);
		$result = [];
		foreach($query as $q){
			foreach($q as $key => $value){
				if($key !== "target_snippets" && strpos($value, ";") !== false){
					$q[$key] = explode(";", $value);
				}
			}
			$result[] = $q;
		}
        for($i = 0; $i < count($result); $i = $i + 1){
            ksort($result[$i]);
        }
		return $result;
	}
	
	public function getDatasets($prefix){
		return $this->getPrefixTable($prefix, 1);
	}

	public function getDetectors($prefix){
		return $this->getPrefixTable($prefix, 2);
	}

	public function getPrefixTable($prefix, $suffix){
		$tables = $this->db->getTables();
		$names = array();
		foreach($tables as $t){
			if(substr($t,0,strlen($prefix)) === $prefix){
				$new = explode("_", $t, 3)[$suffix];
				$add = true;
				foreach($names as $n){
					if($n === $new){
						$add = false;
						break;
					}
				}
				if($add){
					$names[] = $new;
				}
			}
		}
		asort($names);
		return $names;
	}

	public function getAllReviews($table, $project, $version, $id){
		$query = $this->db->getAllReviews($table . "_" . $project . "_" . $version . "_" . $id);
		$reviewer = [];
		if(!$query){
			return [];
		}
		foreach($query as $q){
		    $add = true;
		    foreach($reviewer as $r){
		        if($r === $q['name']){
                    $add = false;
                }
            }
            if($add) {
                $reviewer[] = $q['name'];
            }
		}
		return $reviewer;
	}

	public function getIndex($exp, $dataset, $detector){
	    $table = $exp . "_" . $dataset . "_" . $detector;
		$stats = $this->db->getAllStats($table);
		$projects = [];
		foreach($stats as $s){
			foreach($this->db->getPotentialHits($table, $s['project'], $s['version']) as $hit){
				if($exp !== "ex2"){
					$meta = $this->getMetadata($hit['misuse']);
					$hit['violation_types'] = $meta['violation_types'];
				}
				$reviews = $this->getAllReviews($table, $s['project'], $s['version'], $exp === "ex2" ? $hit['id'] : $hit['misuse']);
				$hit['reviews'] = $reviews;
				$add = true;
				if(array_key_exists('hits', $s)) {
                    foreach ($s['hits'] as $h) {
                        if (($exp === "ex2" && $hit['id'] === $h['id']) || ($exp !== "ex2" && $hit['misuse'] === $h['misuse'])) {
                            $add = false;
                        }
                    }
                }
                if ($add) {
                    $s['hits'][$hit['misuse']] = $hit;
                }
			}
			$projects[$s['project']][$s['version']] = $s;
		}
		ksort($projects);
        foreach($projects as $key => $value){
            ksort($projects[$key]);
            foreach($projects[$key] as $k2 => $value){
                if($projects[$key][$k2] && array_key_exists('hits', $projects[$key][$k2])) {
                    ksort($projects[$key][$k2]['hits']);
                }
            }
        }

		return $projects;
	}

	function custom_sort($a, $b){
	    return $a['misuse'] > $b['misuse'];
    }

}
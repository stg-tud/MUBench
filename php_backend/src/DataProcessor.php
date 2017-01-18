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

	public function getReview($exp, $detector, $project, $version, $misuse, $reviewer){
	    // TODO: use a JOIN for getting all informations with the link tables
		$query = $this->db->getReview($exp, $detector, $project, $version, $misuse, $reviewer);
		$findings = $this->db->getReviewFindings($query['id']);
		if(!$query || !$findings){
		    return [];
        }
		$query['hits'] = [];
		foreach($findings as $finding){
		    $finding['types'] = $this->db->getReviewTypes(intval($finding['id']));
		    $query['hits'][$exp === "ex2" ? $misuse : $finding['rank']] = $finding;
        }
		return $query;
	}

    public function getPatterns($misuse){
		$query = $this->db->getPattern($misuse);
		foreach($query as $q){
			yield $q;
		}
	}

	public function getHits($detector, $project, $version, $misuse, $exp){
        // TODO: load types from a link tables
	    $table = $this->db->getTableName($detector);
	    if(!$table){
	        return [];
        }
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

	public function getDetectors($exp){
		$detectors = $this->db->getDetectorsTables();
		$data = [];
		foreach($detectors as $detector){
		    $this->logger->info("DETECTOR: " . $detector['name']);
		    if($this->db->hasFindingForExp($exp, $detector['id'])){
                $data[] = $detector['name'];
            }
        }
        return $data;
	}

	public function getPrefixTable($prefix, $suffix){
	    // TODO: remove
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

	public function getReviewsMisuse($exp, $detector, $project, $version, $misuse){
		$query = $this->db->getReviewsByIdentifier($exp, $detector, $project, $version, $misuse);
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

	public function getAllReviews(){
	    $query = $this->db->getAllReviews();
        if(!$query){
            return [];
        }
        return $this->unwrapReviews($query);
    }

	public function getTodo($reviewer){
	    // TODO: fix with new review structure
        $exp = ["ex1", "ex2", "ex2"];
        $reviews = $this->getAllReviews();
        $reviewable = [];
        $reviewable[1] = [];
        $reviewable[2] = [];
        $reviewable[3] = [];
        foreach($exp as $ex){
                foreach($this->getDetectors($ex) as $detector){
                    $index = $this->getIndex($ex, $detector);
                    foreach($index as $project => $versions){
                        $count = 0;
                        $alreadyReviewed = false;
                        foreach($reviews[substr($ex, 2)] as $review){
                            if($review['name'] === $reviewer || count >= 2){
                                $alreadyReviewed = true;
                                break;
                            }
                            if(($review['exp'] === $ex && $review['detector'] === $detector
                                && $review['project'] === $project)){
                                $count++;
                            }
                        }
                        if(!$alreadyReviewed && $count < 2){
                            foreach($versions as $version){
                                foreach($version['hits'] as $hit){
                                    $review = [];
                                    $review['exp'] = $ex;
                                    $review['detector'] = $detector;
                                    $review['project'] = $project;
                                    $review['version'] = $version['version'];
                                    $review['misuse'] = $hit['misuse'];
                                    $reviewable[substr($ex, 2)][] = $review;
                                }
                            }
                        }
                    }
                }
            }
        return $reviewable;
    }

	public function getReviewsByReviewer($reviewer){
	    $query = $this->db->getReviewsByReviewer($reviewer);
        if(!$query){
            return [];
        }
        return $this->unwrapReviews($query);
    }

    public function unwrapReviews($query){
	    $reviews = [];
        $reviews[1] = [];
        $reviews[2] = [];
        $reviews[3] = [];
        foreach($query as $q){
//            $review = [];
//            $review['exp'] = $q['exp'];
//            if(false){
//                //$reviews[substr($review['exp'],2)][$q['identifier']]['decision'] = $q['hit'];
//                //$reviews[substr($review['exp'],2)][$q['identifier']]['types'] = array_merge($reviews[substr($review['exp'],2,1)][$q['identifier']]['types'], explode(";", $q['violation_types']));
//                continue;
//            }
//            $review['detector'] = $q['detector'];
//            $review['project'] = $q['project'];
//            $review['version'] = $q['version'];
//            $review['misuse'] = $q['misuse'];
//            // TODO: join decision and types
//            $review['decision'] = "TODO";
//            $review['comment'] = $q['comment'];
//            $review['types'] = ["TODO"];
//            $review['name'] = $q['name'];
//            $reviews[substr($review['exp'],2)][$review['de']] = $review;
        }
        return $reviews;
    }

	public function getIndex($exp, $detector){
	    $table = $this->db->getDetectorTable($detector);
		$stats = $this->db->getAllStats($table);
		$projects = [];
		foreach($stats as $s){
		    $s['hits'] = [];
            foreach($this->db->getPotentialHits($table, $exp, $s['project'], $s['version']) as $hit){
				if($exp !== "ex2"){
					$meta = $this->getMetadata($hit['misuse']);
					$hit['violation_types'] = $meta['violation_types'];
				}
				$reviews = $this->getReviewsMisuse($exp, $detector, $s['project'], $s['version'], $hit['misuse']);
				$hit['reviews'] = $reviews;
				$add = true;
                $id = $hit['misuse'];
				if(array_key_exists('hits', $s)) {
                    foreach ($s['hits'] as $h) {
                        if ($hit['misuse'] === $h['misuse']) {
                            $add = false;
                        }
                    }
                }
                if ($add) {
                    $s['hits'][$id] = $hit;
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

}
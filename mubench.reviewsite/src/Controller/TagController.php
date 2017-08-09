<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;

class TagController
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    public function saveTagForMisuse($tag)
    {
        $tag_id = $this->getOrCreateTag($tag['name'])['id'];
        $experiment = $tag['exp'];
        $detector_id = $tag['detector'];
        $project = $tag['project'];
        $version = $tag['version'];
        $finding = $tag['finding'];
        $this->logger->info("saving tag $tag_id for $experiment, $detector_id, " . $project . ", " . $version . ", " . $finding);
        $misuse_tags = $this->db->getTagsForMisuse($experiment, $detector_id, $project, $version, $finding);
        foreach($misuse_tags as $misuse_tag){
            if($tag_id === $misuse_tag['id']){
                return;
            }
        }
        $this->db->table('misuse_tags')->insert(['exp' => $experiment, 'detector' => $detector_id,
            'project' => $project,
            'version' => $version, 'finding' => $finding, 'tag' => $tag_id]);
    }

    public function getOrCreateTag($name)
    {
        $tag = $this->db->table('tags')->where('name', $name)->get();
        if(!$tag){
            $this->saveNewTag($name);
        }
        return $this->db->table('tags')->where('name', $name)->get()[0];
    }

    public function deleteMisuseTag($experiment, $detector, $project, $version, $finding, $tag)
    {
        $this->logger->info("deleting tag $tag for $detector, $project, $version, $finding");
        $this->db->table('misuse_tags')->where('exp', $experiment)->where('detector', $detector)
            ->where('project', $project)->where('version', $version)->where('finding', $finding)->where('tag', $tag)->delete();
    }

    public function saveNewTag($tag_name)
    {
        $this->db->table('tags')->insert(['name' => $tag_name]);
    }

}
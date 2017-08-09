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

    public function saveTagForMisuse($misuse)
    {
        $tag = $this->getOrCreateTag($misuse['tag']);
        $tag_id = $tag['id'];
        $experiment = $misuse['exp'];
        $detector = $misuse['detector'];
        $project = $misuse['project'];
        $version = $misuse['version'];
        $misuse_id = $misuse['misuse'];
        $this->logger->info("saving tag $tag_id for $experiment, $detector, " . $project . ", " . $version . ", " . $misuse_id);
        $misuse_tags = $this->db->getTagsForMisuse($experiment, $detector, $project, $version, $misuse_id);
        foreach($misuse_tags as $misuse_tag){
            if($tag_id === $misuse_tag['id']){
                return;
            }
        }
        $this->db->table('misuse_tags')->insert(['exp' => $experiment, 'detector' => $detector,
            'project' => $project,
            'version' => $version, 'misuse' => $misuse_id, 'tag' => $tag_id]);
    }

    public function getOrCreateTag($name)
    {
        $tag = $this->db->table('tags')->where('name', $name)->get();
        if(!$tag){
            $this->saveNewTag($name);
        }
        return $this->db->table('tags')->where('name', $name)->get()[0];
    }

    public function deleteMisuseTag($misuse)
    {
        $tag = $misuse['tag'];
        $experiment = $misuse['exp'];
        $detector = $misuse['detector'];
        $project = $misuse['project'];
        $version = $misuse['version'];
        $misuse_id = $misuse['misuse'];
        $this->logger->info("deleting tag $tag for $detector, $project, $version, $misuse_id");
        $this->db->table('misuse_tags')->where('exp', $experiment)->where('detector', $detector)
            ->where('project', $project)->where('version', $version)->where('misuse', $misuse_id)->where('tag', $tag)->delete();
    }

    public function saveNewTag($tag_name)
    {
        $this->db->table('tags')->insert(['name' => $tag_name]);
    }

}
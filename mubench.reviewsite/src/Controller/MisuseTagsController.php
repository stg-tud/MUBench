<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\Model\Detector;
use Slim\Http\Request;
use Slim\Http\Response;

class MisuseTagsController
{

    private $db;
    private $logger;
    private $site_base_url;

    function __construct(DBConnection $db, Logger $logger, $site_base_url)
    {
        $this->db = $db;
        $this->logger = $logger;
        $this->site_base_url = $site_base_url;
    }

    public function add(Request $request, Response $response, array $args) {
        $formData = $request->getParsedBody();
        $experimentId = $formData['exp'];
        $detector = $this->db->getDetector($formData['detector']);
        $projectId = $formData['project'];
        $versionId = $formData['version'];
        $misuseId = $formData['misuse'];
        $tagName = $formData['tag'];
        $this->addTag($experimentId, $detector, $projectId, $versionId, $misuseId, $tagName);
        return $this->redirectBack($response, $formData);
    }

    public function getTags($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        /** @var array $stdClass */
        $stdClass = $this->db->table('misuse_tags')->innerJoin('tags', 'misuse_tags.tag', '=', 'tags.id')
            ->select('id', 'name')->where('exp', $experimentId)->where('detector', $detector->id)
            ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)->get();
        return $stdClass;
    }

    function addTag($experimentId, Detector $detector, $projectId, $versionId, $misuseId, $tagName)
    {
        $tag = $this->getOrCreateTag($tagName);
        $this->logger->info("Tag $experimentId, $detector, $projectId, $versionId, $misuseId with {$tag['id']}:{$tag['name']}");
        // SMELL this should be implemented with insertIgnore or insertOrUpdate, but the SQLite database in the tests can't handle this
        $tagExists = $this->db->table('misuse_tags')->select('COUNT(*)')->innerJoin('tags', 'misuse_tags.tag', '=', 'tags.id')
            ->where('exp', $experimentId)->where('detector', $detector->id)->where('project', $projectId)
            ->where('version', $versionId)->where('misuse', $misuseId)->where('name', $tagName)->first();
        if (!$tagExists) {
            $this->db->table('misuse_tags')->insert(['exp' => $experimentId, 'detector' => $detector->id,
                'project' => $projectId, 'version' => $versionId, 'misuse' => $misuseId, 'tag' => $tag['id']]);
        }
    }

    public function delete(Request $request, Response $response, array $args)
    {
        $formData = $request->getParsedBody();
        $tagName = $formData['tag'];
        $experimentId = $formData['exp'];
        $detector = $this->db->getDetector($formData['detector']);
        $projectId = $formData['project'];
        $versionId = $formData['version'];
        $misuseId = $formData['misuse'];
        $this->deleteTag($experimentId, $detector, $projectId, $versionId, $misuseId, $tagName);
        return $this->redirectBack($response, $formData);
    }

    public function deleteTag($experimentId, Detector $detector, $projectId, $versionId, $misuseId, $tagName)
    {
        $tag = $this->getOrCreateTag($tagName);
        $this->logger->info("Remove tag {$tag['id']}:{$tag['name']} from $experimentId, $detector, $projectId, $versionId, $misuseId");
        $this->db->table('misuse_tags')->where('exp', $experimentId)->where('detector', $detector->id)
            ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)
            ->where('tag', $tag['id'])->delete();
    }

    private function getOrCreateTag($tagName)
    {
        if (!$this->getTag($tagName)) {
            $this->createTag($tagName);
        }
        return $this->getTag($tagName);
    }

    private function getTag($tagName)
    {
        return $this->db->table('tags')->where('name', $tagName)->first();
    }

    private function createTag($tagName)
    {
        $this->db->table('tags')->insert(['name' => $tagName]);
    }

    private function redirectBack(Response $response, $formData)
    {
        return $response->withRedirect("{$this->site_base_url}index.php/{$formData['path']}");
    }

}

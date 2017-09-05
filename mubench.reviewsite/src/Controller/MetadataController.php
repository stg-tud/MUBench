<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;
use MuBench\ReviewSite\Model\Detector;
use Slim\Http\Request;
use Slim\Http\Response;

class MetadataController
{

    private $db;
    private $logger;

    function __construct(DBConnection $db, Logger $logger)
    {
        $this->db = $db;
        $this->logger = $logger;
    }

    function getMetadata($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        if ($experimentId === 'ex1' || $experimentId === 'ex3') {
            $metadata = $this->db->table('metadata')
                ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)->first();

            $types = $this->db->table('misuse_types')->select('types.name')
                ->innerJoin('types', 'misuse_types.type', '=', 'types.id')->where('project', $projectId)
                ->where('version', $versionId)->where('misuse', $misuseId)->get();
            $metadata['violation_types'] = [];
            foreach($types as $type){
                $metadata['violation_types'][] = $type['name'];
            }

            if($experimentId === 'ex1') {
                $metadata['patterns'] = $this->getPatterns($misuseId);
            }
        } else { // if ($experimentId === 'ex2')
            $metadata = ['project' => $projectId, 'version' => $versionId, 'misuse' => $misuseId];
        }

        $metadata['snippets'] = $this->getSnippets($experimentId, $detector, $projectId, $versionId, $misuseId);
        $metadata['tags'] = $this->getTags($experimentId, $detector, $projectId, $versionId, $misuseId);

        return $metadata;
    }

    private function getPatterns($misuse)
    {
        return $this->db->table('patterns')->select(['name', 'code', 'line'])->where('misuse', $misuse)->get();
    }

    // REFACTOR move this into a snippets helper, together with the logic for storing findings snippets
    private function getSnippets($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        $columns = ['line', 'snippet'];
        if ($experimentId === 'ex1' || $experimentId === 'ex3') {
            $query = $this->db->table('meta_snippets')
                ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId);
        } else { // if ($experimentId === 'ex2')
            $columns[] = 'id'; // SMELL meta_findings do not have an id
            $query = $this->db->table('finding_snippets')->where('detector', $detector->id)
                ->where('project', $projectId)->where('version', $versionId)->where('finding', $misuseId);
        }
        return $query->select($columns)->get();
    }

    // REFACTOR move this into a tags helper, together with the logic for adding/removing tags
    private function getTags($experimentId, Detector $detector, $projectId, $versionId, $misuseId)
    {
        return $this->db->table('misuse_tags')->innerJoin('tags', 'misuse_tags.tag', '=', 'tags.id')
            ->select('id', 'name')->where('exp', $experimentId)->where('detector', $detector->id)
            ->where('project', $projectId)->where('version', $versionId)->where('misuse', $misuseId)->get();
    }

    public function update(Request $request, Response $response, array $args)
    {
        $metadata = $this->decodeJsonBody($request);
        if (!$metadata) {
            return $this->respondWithError($response, $this->logger, 400, 'empty: ' . print_r($request->getBody(), true));
        }
        foreach ($metadata as $misuseMetadata) {
            $projectId = $misuseMetadata['project'];
            $versionId = $misuseMetadata['version'];
            $misuseId = $misuseMetadata['misuse'];
            $description = $misuseMetadata['description'];
            $fix = $misuseMetadata['fix'];
            $location = $misuseMetadata['location'];
            $violationTypes = $misuseMetadata['violation_types'];
            $patterns = $misuseMetadata['patterns'];
            $targetSnippets = $misuseMetadata['target_snippets'];

            $this->updateMetadata($misuseId, $projectId, $versionId, $description, $fix, $location, $violationTypes, $patterns, $targetSnippets);
        }
        return $response->withStatus(200);
    }

    // REFACTOR remove this, once it is no longer used
    public function processMetaData($misuseMetadata)
    {
        $projectId = $misuseMetadata['project'];
        $versionId = $misuseMetadata['version'];
        $misuseId = $misuseMetadata['misuse'];
        $description = $misuseMetadata['description'];
        $fix = $misuseMetadata['fix'];
        $location = $misuseMetadata['location'];
        $violationTypes = $misuseMetadata['violation_types'];
        $patterns = $misuseMetadata['patterns'];
        $targetSnippets = $misuseMetadata['target_snippets'];

        $this->updateMetadata($misuseId, $projectId, $versionId, $description, $fix, $location, $violationTypes, $patterns, $targetSnippets);
    }

    function updateMetadata($misuseId, $projectId, $versionId, $description, $fix, $location, $violationTypes, $patterns, $targetSnippets)
    {
        $this->deleteMetadata($misuseId);
        $this->saveMetadata($projectId, $versionId, $misuseId, $description, $fix, $location);
        $this->saveViolationTypes($projectId, $versionId, $misuseId, $violationTypes);
        $this->savePatterns($misuseId, $patterns);
        $this->saveTargetSnippets($misuseId, $projectId, $versionId, $targetSnippets);
    }

    private function deleteMetadata($misuseId)
    {
        $this->logger->info("delete metadata for misuse $misuseId");
        $this->db->table('metadata')->where('misuse', $misuseId)->delete();
        $this->db->table('patterns')->where('misuse', $misuseId)->delete();
    }

    private function saveMetadata($projectId, $versionId, $misuseId, $description, $fix, $location)
    {
        $this->logger->info("saving metadata for $projectId, $versionId, $misuseId");
        $this->db->table('metadata')->insert(['project' => $projectId, 'version' => $versionId, 'misuse' => $misuseId,
            'description' => $description, 'fix_description' => $fix['description'], 'diff_url' => $fix['diff-url'],
            'file' => $location['file'], 'method' => $location['method']]);
    }

    private function saveViolationTypes($projectId, $versionId, $misuseId, $violationTypes)
    {
        $this->logger->info("saving violation types for $projectId, $versionId, $misuseId");
        foreach ($violationTypes as $type_name) {
            $violation_type = $this->getOrCreateViolationType($type_name);
            $this->logger->info(print_r($violation_type, true));
            $this->db->table('misuse_types')->insert(['project' => $projectId, 'version' => $versionId, 'misuse' => $misuseId, 'type' => $violation_type['id']]);
        }
    }

    private function getOrCreateViolationType($violationType)
    {
        $type = $this->db->table('types')->where('name', $violationType)->first();
        if(!$type) {
            $this->db->table('types')->insert(['name' => $violationType]);
            $type = $this->db->table('types')->where('name', $violationType)->first();
        }
        return $type;
    }

    private function savePatterns($misuseId, $patterns)
    {
        if ($patterns) {
            foreach ($patterns as $pattern) {
                $this->db->table('patterns')->insert(['misuse' => $misuseId, 'name' => $pattern['id'],
                    'code' => $pattern['snippet']['code'], 'line' => $pattern['snippet']['first_line']]);
            }
        }
    }

    private function saveTargetSnippets($misuseId, $projectId, $versionId, $targetSnippets)
    {
        if ($targetSnippets) {
            foreach ($targetSnippets as $snippet) {
                $this->db->table('meta_snippets')->insert(['project' => $projectId, 'version' => $versionId,
                    'misuse' => $misuseId, 'snippet' => $snippet['code'], 'line' => $snippet['first_line_number']]);
            }
        }
    }

    function decodeJsonBody(Request $request) {
        $requestBody = $request->getParsedBody();
        $body = json_decode($requestBody, true);
        if ($body) return $body;
        $body = json_decode($request->getBody(), true);
        if ($body) return $body;
        $body = json_decode($_POST['data'], true);
        return $body;
    }

    function respondWithError(Response $response, Logger $logger, $code, $message) {
        $logger->error($message);
        return $response->withStatus($code)->write($message);
    }
}

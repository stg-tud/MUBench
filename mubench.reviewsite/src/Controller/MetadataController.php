<?php

namespace MuBench\ReviewSite\Controller;

use Monolog\Logger;
use MuBench\ReviewSite\DBConnection;
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

    public function update(Request $request, Response $response, array $args)
    {
        $metadata = $this->decodeJsonBody($request);
        if (!$metadata) {
            return $this->respondWithError($response, $this->logger, 400, "empty: " . print_r($request->getBody(), true));
        }
        foreach ($metadata as $misuseMetadata) {
            $this->processMetaData($misuseMetadata);
        }
        return $response->withStatus(200);
    }

    // REFACTOR inline this into the method above, once it is no longer used
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

    private function updateMetadata($misuseId, $projectId, $versionId, $description, $fix, $location, $violationTypes, $patterns, $targetSnippets)
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
        $body = json_decode($_POST["data"], true);
        return $body;
    }

    function respondWithError(Response $response, Logger $logger, $code, $message) {
        $logger->error($message);
        return $response->withStatus($code)->write($message);
    }
}

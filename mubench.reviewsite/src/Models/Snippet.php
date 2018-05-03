<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Snippet extends Model
{
    public $timestamps = false;
    public $fillable = ['project_muid', 'version_muid', 'misuse_muid', 'file', 'line', 'snippet', 'detector_muid'];

    public function setFileAttribute($file)
    {
        $this->attributes['file'] = self::hashFile($file);
    }

    public function scopeOf($query, $projectId, $versionId, $misuseId, $file) {
        return $query->where(['project_muid'=> $projectId, 'version_muid' => $versionId, 'misuse_muid' => $misuseId,
            'file' => self::hashFile($file)]);
    }

    public static function createIfNotExists($projectId, $versionId, $misuseId, $file, $line, $code, $detectorId = "")
    {
        $query = Snippet::of($projectId, $versionId, $misuseId, $file)->where('line', $line);
        if($detectorId !== ""){
            $query->where('detector_muid', $detectorId);
        }
        $snippet = $query->first();
        if (!$snippet) {
            Snippet::create([
                'project_muid'=> $projectId, 'version_muid' => $versionId, 'misuse_muid' => $misuseId,
                'file' => $file, 'line' => $line, 'snippet' => $code, 'detector_muid' => $detectorId
            ]);
        }
    }

    private static function hashFile($file)
    {
        return hash('md5', $file);
    }
}

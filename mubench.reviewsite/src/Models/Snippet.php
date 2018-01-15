<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Snippet extends Model
{
    public $timestamps = false;
    public $fillable = ['project_muid', 'version_muid', 'misuse_muid', 'file', 'line', 'snippet'];

    public function setFileAttribute($file)
    {
        $this->attributes['file'] = self::hashFile($file);
    }

    public function scopeOf($query, $projectId, $versionId, $misuseId, $file) {
        return $query->where([
            'project_muid'=> $projectId, 'version_muid' => $versionId, 'misuse_muid' => $misuseId,
            'file' => self::hashFile($file)
        ]);
    }

    public static function createIfNotExists($projectId, $versionId, $misuseId, $file, $line, $code)
    {
        if (!Snippet::of($projectId, $versionId, $misuseId, $file)->where('line', $line)->first()) {
            Snippet::create([
                'project_muid'=> $projectId, 'version_muid' => $versionId, 'misuse_muid' => $misuseId,
                'file' => $file, 'line' => $line, 'snippet' => $code
            ]);
        }
    }

    private static function hashFile($file)
    {
        return hash('md5', $file);
    }
}

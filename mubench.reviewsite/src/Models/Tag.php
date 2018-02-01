<?php

namespace MuBench\ReviewSite\Models;


use Illuminate\Database\Eloquent\Model;

class Tag extends Model
{

    protected $fillable = ['name', 'color'];
    public $timestamps = false;

    public function misuses()
    {
        return $this->belongsToMany(Misuse::class, 'misuse_tags', 'tag_id', 'misuse_id');
    }

    public function getFontColor()
    {
        $rgb = $this->getColorAsRGB();
        $yiq = (($rgb[0]*299)+($rgb[1]*587)+($rgb[2]*114))/1000;
        return ($yiq >= 128) ? 'black' : 'white';
    }

    private function getColorAsRGB(){
        return array_map(function($hex) {
            return hexdec($hex);
        }, $this->getRawHexValues());
    }

    private function getRawHexValues(){
        // #abc or #aabbcc, everything between gets mapped on #abc
        return strlen($this->color) == 6 ? str_split(substr($this->color, 1), 2)
            : array_map(function($color) { return str_repeat($color, 2); }, str_split(substr($this->color, 1, 3), 1));
    }
}

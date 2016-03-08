#!/bin/sh

repository=$1
revision=$2
dirtarget=$3

mkdir $dirtarget
svn checkout --revision $revision $repository $dirtarget

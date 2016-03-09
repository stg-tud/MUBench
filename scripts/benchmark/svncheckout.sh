#!/bin/sh

repository=$1
revision=$2
dirtarget=$3

if [ ! -d "$dirtarget"]; then
  mkdir "$dirtarget"
fi

svn checkout --revision $revision $repository $dirtarget

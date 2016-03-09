#!/bin/sh

repository=$1
commithash=$2
dirtarget=$3

if [ ! -d "$dirtarget" ]; then
  mkdir $dirtarget
fi

git clone $repository $dirtarget
cd $dirtarget
git checkout $commithash

#!/bin/sh

repository=$1
commithash=$2
dirtarget=$3

mkdir $dirtarget
git clone $repository $dirtarget
cd $dirtarget
git checkout $commithash

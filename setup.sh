#!/bin/bash

mkdir logs
echo  "local path is $BUILD_REPOSITORY_LOCALPATH"
echo "##vso[task.setvariable variable=panpath]$BUILD_REPOSITORY_LOCALPATH/panoptes"
echo $PANPATH
cd $PANPATH

#!/bin/bash

echo  "local path is $PATH"
echo ls
echo "##vso[task.setvariable variable=panpath]$BUILD_REPOSITORY_LOCALPATH/panoptes"
echo "$PANPATH"
cd $PANPATH

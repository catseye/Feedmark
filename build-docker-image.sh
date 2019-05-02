#!/bin/sh

# After building the image, you can run feedmark from within it like:
#
# docker run --user $(id -u):$(id -g) -i -t -v "${PWD}:/mnt/host" feedmark \
#        feedmark "eg/Ancient Llama Sightings.md" --output-atom samplefeed.xml
#

PROJECT=feedmark
VERSION=0.9

rm -rf src/${PROJECT}/*.pyc src/${PROJECT}/__pycache__
docker container prune
docker rmi catseye/${PROJECT}:${VERSION}
docker rmi ${PROJECT}
docker build -t ${PROJECT} .
docker tag ${PROJECT} catseye/${PROJECT}:${VERSION}

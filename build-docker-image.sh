#!/bin/sh

# After building the image, you can run feedmark from within it like:
#
# docker run --user $(id -u):$(id -g) -i -t -v "${PWD}:/mnt/host" feedmark \
#        feedmark "eg/Ancient Llama Sightings.md" --output-atom samplefeed.xml
#

rm -rf src/feedmark/*.pyc src/feedmark/__pycache__
docker container prune
docker rmi catseye/feedmark:0.8
docker rmi feedmark
docker build -t feedmark .
docker tag feedmark catseye/feedmark:0.8

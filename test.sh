#!/bin/sh

# Very, very rudimentary tests.

./bin/feedmark eg/*.md || exit 1
./bin/feedmark "eg/Recent Llama Sightings.md" --output-atom=feed.xml || exit 1
grep '<id>http://example.com/llama.xml/2 Llamas Spotted Near Mall</id>' feed.xml > /dev/null || exit 1
rm -f feed.xml
./bin/feedmark eg/*Sightings*.md --check-against=eg/schema/Llama\ sighting.md || exit 1

echo "All tests pass."

#!/bin/sh

# Very, very rudimentary tests.

# 1----
./bin/feedmark eg/*.md || exit 1

# 2----
./bin/feedmark "eg/Recent Llama Sightings.md" --output-atom=feed.xml || exit 1
grep '<id>http://example.com/llama.xml/2 Llamas Spotted Near Mall</id>' feed.xml > /dev/null || exit 1
rm -f feed.xml

# 3----
./bin/feedmark eg/*Sightings*.md --check-against=eg/schema/Llama\ sighting.md || exit 1

# 4----
./bin/feedmark "eg/Recent Llama Sightings.md" --output-html >feed.html || exit 1
grep '<h3 id="a-possible-llama-under-the-bridge">A Possible Llama Under the Bridge</h3>' feed.html > /dev/null || exit 1
rm -f feed.html

echo "All tests pass."

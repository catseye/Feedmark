import unittest

from subprocess import check_call


class TestFeedmark(unittest.TestCase):

    def test_load_documents(self):
        check_call('./bin/feedmark eg/*.md', shell=True)

    def test_atom_feed(self):
        check_call('./bin/feedmark "eg/Recent Llama Sightings.md" --output-atom=feed.xml', shell=True)
        check_call('''grep '<id>http://example.com/llama.xml/2 Llamas Spotted Near Mall</id>' feed.xml >/dev/null''', shell=True)
        #check_call('rm -f feed.xml')

    def test_schema(self):
        check_call('./bin/feedmark eg/*Sightings*.md --check-against=eg/schema/Llama\ sighting.md', shell=True)

    # # 4----
    # ./bin/feedmark "eg/Recent Llama Sightings.md" --output-html >feed.html || exit 1
    # grep '<h3 id="a-possible-llama-under-the-bridge">A Possible Llama Under the Bridge</h3>' feed.html > /dev/null || exit 1
    # rm -f feed.html
    # 
    # # 5----
    # ./bin/feedmark "eg/Ancient Llama Sightings.md" --output-json >feed.json || exit 1
    # grep '"title": "Ancient Llama Sightings"' feed.json > /dev/null || exit 1
    # grep '"title": "Maybe sighting the llama"' feed.json > /dev/null || exit 1
    # grep '"date": "Jan 1 1984 12:00:00"' feed.json > /dev/null || exit 1
    # rm -f feed.json


if __name__ == '__main__':
    unittest.main()

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

    def test_output_html(self):
        check_call('./bin/feedmark "eg/Recent Llama Sightings.md" --output-html >feed.html', shell=True)
        check_call('''grep '<h3 id="a-possible-llama-under-the-bridge">A Possible Llama Under the Bridge</h3>' feed.html > /dev/null''', shell=True)
        #check_call('rm -f feed.html')

    def test_output_json(self):
        check_call('./bin/feedmark "eg/Ancient Llama Sightings.md" --output-json >feed.json', shell=True)
        check_call('''grep '"title": "Ancient Llama Sightings"' feed.json > /dev/null''', shell=True)
        check_call('''grep '"title": "Maybe sighting the llama"' feed.json > /dev/null''', shell=True)
        check_call('''grep '"date": "Jan 1 1984 12:00:00"' feed.json > /dev/null''', shell=True)
        #check_call('rm -f feed.json')


if __name__ == '__main__':
    unittest.main()

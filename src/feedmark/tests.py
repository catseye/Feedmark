import unittest

from os import unlink
from subprocess import check_call

from feedmark.loader import read_document_from
from feedmark.checkers import Schema


class TestFeedmarkCommandLine(unittest.TestCase):

    def assert_file_contains(self, filename, text):
        with open(filename, 'r') as f:
            contents = f.read()
        self.assertIn(text, contents)

    def test_atom_feed(self):
        check_call('./bin/feedmark "eg/Recent Llama Sightings.md" --output-atom=feed.xml', shell=True)
        self.assert_file_contains('feed.xml', '<id>http://example.com/llama.xml/2 Llamas Spotted Near Mall</id>')
        unlink('feed.xml')

    def test_schema(self):
        check_call('./bin/feedmark eg/*Sightings*.md --check-against=eg/schema/Llama\ sighting.md', shell=True)

    def test_output_html(self):
        check_call('./bin/feedmark "eg/Recent Llama Sightings.md" --output-html >feed.html', shell=True)
        self.assert_file_contains('feed.html', '<h3 id="a-possible-llama-under-the-bridge">A Possible Llama Under the Bridge</h3>')
        unlink('feed.html')

    def test_output_json(self):
        check_call('./bin/feedmark "eg/Ancient Llama Sightings.md" --output-json >feed.json', shell=True)
        self.assert_file_contains('feed.json', '"title": "Ancient Llama Sightings"')
        self.assert_file_contains('feed.json', '"title": "Maybe sighting the llama"')
        self.assert_file_contains('feed.json', '"date": "Jan 1 1984 12:00:00"')
        unlink('feed.json')


class TestFeedmarkInternals(unittest.TestCase):

    def test_load_documents(self):
        doc1 = read_document_from('eg/Ancient Llama Sightings.md')
        self.assertEqual(doc1.title, "Ancient Llama Sightings")
        doc2 = read_document_from('eg/Recent Llama Sightings.md')
        self.assertEqual(doc2.title, "Recent Llama Sightings")
        self.assertEqual(len(doc2.sections), 3)

    def test_schema(self):
        schema_doc = read_document_from('eg/schema/Llama sighting.md')
        schema = Schema(schema_doc)

        doc1 = read_document_from('eg/Ancient Llama Sightings.md')
        doc2 = read_document_from('eg/Recent Llama Sightings.md')
        results = schema.check_documents([doc1, doc2])
        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main()

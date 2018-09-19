import unittest

import json
from os import unlink
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from subprocess import check_call
import sys

from feedmark.checkers import Schema
from feedmark.main import main
from feedmark.loader import read_document_from


class TestFeedmarkCommandLine(unittest.TestCase):

    def setUp(self):
        super(TestFeedmarkCommandLine, self).setUp()
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.saved_stdout
        super(TestFeedmarkCommandLine, self).tearDown()

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
        self.maxDiff = None
        result = main(['eg/Ancient Llama Sightings.md', '--output-json'])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(data, {
            u'documents': [
                {
                    u'filename': u'eg/Ancient Llama Sightings.md',
                    u'title': u'Ancient Llama Sightings',
                    u'preamble': u'',
                    u'properties': data['documents'][0]['properties'],
                    u'sections': data['documents'][0]['sections'],
                }
            ]
        })


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

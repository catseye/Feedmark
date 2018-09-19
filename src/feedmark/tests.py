
import unittest

import json
from os import unlink
import sys

from feedmark.checkers import Schema
from feedmark.main import main
from feedmark.loader import read_document_from
from feedmark.utils import StringIO


class TestFeedmarkCommandLine(unittest.TestCase):

    def setUp(self):
        super(TestFeedmarkCommandLine, self).setUp()
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()
        self.maxDiff = None

    def tearDown(self):
        sys.stdout = self.saved_stdout
        super(TestFeedmarkCommandLine, self).tearDown()

    def assert_file_contains(self, filename, text):
        with open(filename, 'r') as f:
            contents = f.read()
        self.assertIn(text, contents)

    def test_atom_feed(self):
        main(["eg/Recent Llama Sightings.md", '--output-atom=feed.xml'])
        self.assert_file_contains('feed.xml', '<id>http://example.com/llama.xml/2 Llamas Spotted Near Mall</id>')
        unlink('feed.xml')

    def test_schema(self):
        main(["eg/Recent Llama Sightings.md", "eg/Ancient Llama Sightings.md", '--check-against=eg/schema/Llama sighting.md'])
        output = sys.stdout.getvalue()
        self.assertEqual(output, '')

    def test_schema_failure(self):
        with self.assertRaises(SystemExit) as ar:
            main(["eg/Ill-formed Llama Sightings.md", '--check-against=eg/schema/Llama sighting.md'])
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(data, [
            {
                u'document': u'Ill-formed Llama Sightings',
                u'result': [[u'extra', u'excuse'], [u'missing', u'date']],
                u'section': u'Definite llama sighting with no date'
            }
        ])

    def test_output_html(self):
        main(["eg/Recent Llama Sightings.md", "--output-html"])
        output = sys.stdout.getvalue()
        self.assertIn('<h3 id="a-possible-llama-under-the-bridge">A Possible Llama Under the Bridge</h3>', output)

    def test_output_json(self):
        main(['eg/Ancient Llama Sightings.md', '--output-json'])
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

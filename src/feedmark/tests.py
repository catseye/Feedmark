import unittest

import json
import os
import sys
from subprocess import check_call
from tempfile import mkdtemp

from feedmark.checkers import Schema
from feedmark.main import main
from feedmark.loader import read_document_from
from feedmark.utils import StringIO


class TestFeedmarkFileCreation(unittest.TestCase):

    def setUp(self):
        super(TestFeedmarkFileCreation, self).setUp()
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()
        self.maxDiff = None
        self.dirname = mkdtemp()
        self.prevdir = os.getcwd()
        os.chdir(self.dirname)

    def tearDown(self):
        os.chdir(self.prevdir)
        check_call("rm -rf {}".format(self.dirname), shell=True)
        sys.stdout = self.saved_stdout
        super(TestFeedmarkFileCreation, self).tearDown()

    def assert_file_contains(self, filename, text):
        with open(filename, 'r') as f:
            contents = f.read()
        self.assertIn(text, contents)

    def test_atom_feed(self):
        main(["{}/eg/Recent Llama Sightings.md".format(self.prevdir), '--output-atom=feed.xml'])
        self.assert_file_contains('feed.xml', '<id>http://example.com/llama.xml/2 Llamas Spotted Near Mall</id>')
        self.assert_file_contains('feed.xml',
            'https://github.com/catseye/Feedmark/blob/master/eg/Recent%20Llama%20Sightings.md#2-llamas-spotted-near-mall'
        )
        os.unlink('feed.xml')


class TestFeedmarkCommandLine(unittest.TestCase):

    def setUp(self):
        super(TestFeedmarkCommandLine, self).setUp()
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()
        self.maxDiff = None

    def tearDown(self):
        sys.stdout = self.saved_stdout
        super(TestFeedmarkCommandLine, self).tearDown()

    def test_schema(self):
        main(["eg/Recent Llama Sightings.md", "eg/Ancient Llama Sightings.md", '--check-against=eg/schema/Llama sighting.md'])
        output = sys.stdout.getvalue()
        self.assertEqual(output, '')

    def test_schema_failure(self):
        with self.assertRaises(SystemExit):
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
        self.assertDictEqual(data['documents'][0]['properties'], {
            u'author': u'Alfred J. Prufrock',
            u'link-target-url': u'https://github.com/catseye/Feedmark/blob/master/eg/Ancient%20Llama%20Sightings.md',
            u'url': u'http://example.com/old_llama.xml'
        })
        self.assertEqual(data['documents'][0]['sections'], [
            {
                u'body': data['documents'][0]['sections'][0]['body'],
                u'images': [],
                u'properties': {u'date': u'Jan 1 1984 12:00:00'},
                u'title': u'Maybe sighting the llama',
                u'anchor': u'maybe-sighting-the-llama',
            }
        ])
        self.assertIn(u'It was a possible llama sighting.\n\n', data['documents'][0]['sections'][0]['body'])

    def test_output_htmlized_json(self):
        main(['eg/Referenced Llama Sightings.md', '--output-json', '--htmlized-json'])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(data, {
            u'documents': [
                {
                    u'filename': u'eg/Referenced Llama Sightings.md',
                    u'title': u'Referenced Llama Sightings',
                    u'preamble': u'<p>Some <strong>llamas</strong> have been <a href="spotted.html">spotted</a> recently.</p>',
                    u'properties': data['documents'][0]['properties'],
                    u'sections': data['documents'][0]['sections'],
                }
            ]
        })
        self.assertEqual(
            data['documents'][0]['sections'][0]['body'],
            u"<p>I have strong opinions about this.  It's a <em>shame</em> more llamas aren't\nbeing spotted.  "
             "Sometimes they are <strong>striped</strong>, it's true, but<br />\nwhen<br />\nthey are, "
             "<a href=\"https://daringfireball.net/projects/markdown/\">Markdown</a>\ncan be used.</p>\n"
             "<p>To <a href=\"https://en.wikipedia.org/wiki/Site\">site</a> them.</p>\n<p>Sight them, sigh.</p>"
        )
        # note that property values are bare HTML: there is no surrounding <p></p> or other element
        self.assertEqual(
            data['documents'][0]['properties']['hopper'],
            '<a href="https://en.wikipedia.org/wiki/Stephen_Hopper">Stephen</a>'
        )
        self.assertEqual(
            data['documents'][0]['properties']['spotted'],
            [u'<a href="mall.html">the mall</a>', u'<a href="beach.html">the beach</a>']
        )
        self.assertEqual(
            data['documents'][0]['sections'][0]['properties']['hopper'],
            '<a href="https://en.wikipedia.org/wiki/Grace_Hopper">Grace</a>'
        )
        self.assertEqual(
            data['documents'][0]['sections'][0]['properties']['spotted'],
            [u'<a href="mall.html">the mall</a>', u'<a href="lumberyard.html">the lumberyard</a>']
        )

    def test_output_unordered_json(self):
        main(['eg/Referenced Llama Sightings.md', '--output-json'])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(data['documents'][0]['properties'], {
            u'author': u'Alfred J. Prufrock',
            u'link-target-url': u'https://github.com/catseye/Feedmark/blob/master/eg/Referenced%20Llama%20Sightings.md',
            u'url': u'http://example.com/refllama.xml',
            u'hopper': u'[Stephen](https://en.wikipedia.org/wiki/Stephen_Hopper)',
            u'spotted': [u'[the mall][]', u'[the beach](beach.html)'],
        })
        self.assertDictEqual(data['documents'][0]['sections'][0]['properties'], {
            u'date': u'Nov 1 2016 09:00:00',
            u'hopper': u'[Grace](https://en.wikipedia.org/wiki/Grace_Hopper)',
            u'spotted': [u'[the mall][]', u'[the lumberyard](lumberyard.html)'],
        })

    def test_output_ordered_json(self):
        main(['eg/Referenced Llama Sightings.md', '--output-json', '--ordered-json'])
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(data['documents'][0]['properties'], [
            [u'author', u'Alfred J. Prufrock'],
            [u'url', u'http://example.com/refllama.xml'],
            [u'link-target-url', u'https://github.com/catseye/Feedmark/blob/master/eg/Referenced%20Llama%20Sightings.md'],
            [u'hopper', u'[Stephen](https://en.wikipedia.org/wiki/Stephen_Hopper)'],
            [u'spotted', [u'[the mall][]', u'[the beach](beach.html)']],
        ])
        self.assertEqual(data['documents'][0]['sections'][0]['properties'], [
            [u'date', u'Nov 1 2016 09:00:00'],
            [u'hopper', u'[Grace](https://en.wikipedia.org/wiki/Grace_Hopper)'],
            [u'spotted', [u'[the mall][]', u'[the lumberyard](lumberyard.html)']]
        ])

    def test_output_refdex(self):
        main(['eg/Recent Llama Sightings.md', 'eg/Ancient Llama Sightings.md', '--output-refdex'])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(data, {
            "2 Llamas Spotted Near Mall": {
                "anchor": "2-llamas-spotted-near-mall",
                "filename": "eg/Recent Llama Sightings.md"
            },
            "A Possible Llama Under the Bridge": {
                "anchor": "a-possible-llama-under-the-bridge",
                "filename": "eg/Recent Llama Sightings.md"
            },
            "Llamas: It's Time to Spot Them": {
                "anchor": "llamas-its-time-to-spot-them",
                "filename": "eg/Recent Llama Sightings.md"
            },
            "Maybe sighting the llama": {
                "anchor": "maybe-sighting-the-llama",
                "filename": "eg/Ancient Llama Sightings.md"
            }
        })

    def test_input_refdex_output_markdown(self):
        main(['eg/Ill-formed Llama Sightings.md', '--input-refdex', 'eg/refdex.json', '--output-markdown'])
        output = sys.stdout.getvalue()
        self.assertIn('[2 Llamas Spotted Near Mall]: eg/Recent%20Llama%20Sightings.md#2-llamas-spotted-near-mall', output)

    def test_output_links(self):
        main(['eg/Ill-formed Llama Sightings.md', '--output-links'])
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(data, [
            {
                u'document': u'Ill-formed Llama Sightings',
                u'name': u'2 Llamas Spotted Near Mall',
                u'section': u'Definite llama sighting with no date',
                u'url': u'TK'
            },
            {
                u'document': u'Ill-formed Llama Sightings',
                u'section': u'Definite llama sighting with no date',
                u'url': u'https://tcrf.net/The_Cutting_Room_Floor'
            }
        ])


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

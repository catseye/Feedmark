from argparse import ArgumentParser
import codecs
from datetime import datetime
import sys

import atomize
import markdown

from feedmark.parser import Parser


def extract_feed_entries(document):
    properties = {}

    properties['title'] = document.title
    properties['author'] = document.properties['author']
    properties['url'] = document.properties['url']

    entries = []
    for section in document.sections:
        guid = properties['url'] + "/" + section.title
        updated = section.publication_date

        summary = atomize.Summary(markdown.markdown(section.body), content_type='html')

        #links = [atomize.Link(section.link, content_type='text/html',
        #                      rel='alternate')]
        links = []
        entry = atomize.Entry(title=section.title, guid=guid, updated=updated,
                              summary=summary, links=links)
        entries.append(entry)

    return entries, properties


def feedmark_atomize(documents, out_filename, limit=None):
    entries = []
    properties = {}

    for document in documents:
        these_entries, these_properties = extract_feed_entries(document)
        properties.update(these_properties)  # TODO: something more elegant than this
        entries.extend(these_entries)

    if limit and len(entries) > limit:
        entries = entries[:limit]

    assert properties['author'], "Need author"

    feed = atomize.Feed(
        author=properties['author'],
        title=properties['title'],
        updated=datetime.utcnow(),
        guid=properties['url'],
        self_link=properties['url'],
        entries=entries
    )

    feed.write_file(out_filename)


def main(args):
    argparser = ArgumentParser()

    argparser.add_argument('input_files', nargs='+', metavar='FILENAME', type=str,
        help='Markdown files containing the embedded entries'
    )
    argparser.add_argument('--output-atom', metavar='FILENAME', type=str,
        help='Construct an Atom XML feed from the entries and write it out to this file'
    )

    options = argparser.parse_args(sys.argv[1:])

    documents = []

    for filename in options.input_files:
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        parser = Parser(markdown_text)
        document = parser.parse_document()
        documents.append(document)

    if options.output_atom:
        feedmark_atomize(documents, options.output_atom)


if __name__ == '__main__':
    main(sys.argv[1:])

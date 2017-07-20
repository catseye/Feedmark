from argparse import ArgumentParser
import codecs
from datetime import datetime
import sys

import atomize
import markdown

from feedmark.parser import Parser


def extract_entries(markdown_text, properties):
    """`properties` should be a dict-like object; it will be populated by the properties
    of the set of entries found in the document."""

    parser = Parser(markdown_text)
    document = parser.parse_document()

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

    return entries


def feedmark_atomize(in_filenames, out_filename, limit=None):
    entries = []
    properties = {}
    for in_filename in in_filenames:
        with codecs.open(in_filename, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        these_properties = {}
        these_entries = extract_entries(markdown_text, these_properties)
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

    argparser.add_argument('infiles', nargs='+', metavar='FILENAME', type=str,
        help='Markdown files containing the embedded entries'
    )
    argparser.add_argument('--output-atom', metavar='FILENAME', type=str,
        help='Construct an Atom XML feed from the entries and write it out to this file'
    )

    options = argparser.parse_args(sys.argv[1:])

    if options.output_atom:
        feedmark_atomize(options.infiles, options.output_atom)


if __name__ == '__main__':
    main(sys.argv[1:])

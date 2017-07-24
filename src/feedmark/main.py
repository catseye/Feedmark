from argparse import ArgumentParser
import codecs
import sys

from feedmark.atomizer import feedmark_atomize
from feedmark.htmlizer import feedmark_htmlize
from feedmark.feeds import extract_sections
from feedmark.parser import Parser


def main(args):
    argparser = ArgumentParser()

    argparser.add_argument('input_files', nargs='+', metavar='FILENAME', type=str,
        help='Markdown files containing the embedded entries'
    )
    argparser.add_argument('--by-property', action='store_true',
        help='Display a list of all properties found and list the entries they were found on'
    )
    argparser.add_argument('--dump-entries', action='store_true',
        help='Display a summary of the entries on standard output'
    )
    argparser.add_argument('--output-atom', metavar='FILENAME', type=str,
        help='Construct an Atom XML feed from the entries and write it out to this file'
    )
    argparser.add_argument('--output-html-snippet', action='store_true',
        help='Construct a snippet of HTML from the entries and write it to stdout'
    )
    argparser.add_argument('--limit', metavar='COUNT', type=int, default=None,
        help='Process no more than this many entries when making an Atom or HTML feed'
    )

    options = argparser.parse_args(sys.argv[1:])

    documents = []

    for filename in options.input_files:
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        parser = Parser(markdown_text)
        document = parser.parse_document()
        documents.append(document)

    def write(s):
        print(s.encode('utf-8'))

    if options.dump_entries:
        for document in documents:
            for section in document.sections:
                write(section.title)
                for (name, url) in section.images:
                    write(u'    !{}: {}'.format(name, url))
                for key, value in section.properties.iteritems():
                    if isinstance(value, list):
                        write(u'    {}@'.format(key))
                        for subitem in value:
                            write(u'        {}'.format(subitem))
                    else:
                        write(u'    {}: {}'.format(key, value))

    if options.by_property:
        by_property = {}
        for document in documents:
            for section in document.sections:
                for key, value in section.properties.iteritems():
                    if isinstance(value, list):
                        key = u'{}@'.format(key)
                    by_property.setdefault(key, set()).add(section.title)
        for property_name, entry_set in sorted(by_property.iteritems()):
            write(property_name)
            for entry_name in sorted(entry_set):
                write(u'    {}'.format(entry_name))

    if options.output_html_snippet:
        s = feedmark_htmlize(documents, limit=options.limit)
        write(s)

    if options.output_atom:
        feedmark_atomize(documents, options.output_atom, limit=options.limit)


if __name__ == '__main__':
    main(sys.argv[1:])

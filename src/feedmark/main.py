from argparse import ArgumentParser
import codecs
import json
import sys

from feedmark.atomizer import feedmark_atomize
from feedmark.feeds import extract_sections
from feedmark.parser import Parser


def main(args):
    argparser = ArgumentParser()

    argparser.add_argument('input_files', nargs='+', metavar='FILENAME', type=str,
        help='Markdown files containing the embedded entries'
    )

    argparser.add_argument('--by-property', action='store_true',
        help='Output JSON containing a list of all properties found and the entries they were found on'
    )
    argparser.add_argument('--dump-entries', action='store_true',
        help='Display a summary of the entries on standard output'
    )

    argparser.add_argument('--archive-links-to', metavar='DIRNAME', type=str, default=None,
        help='Download a copy of all web objects linked to from the entries'
    )
    argparser.add_argument('--check-links', action='store_true',
        help='Check if web objects linked to from the entries exist'
    )
    argparser.add_argument('--check-against-schema', metavar='FILENAME', type=str, default=None,
        help='Check if entries have the properties specified by this schema.  This schema will '
             'also provide hints (such as ordering of properties) when outputting Markdown or HTML.'
    )

    argparser.add_argument('--output-atom', metavar='FILENAME', type=str,
        help='Construct an Atom XML feed from the entries and write it out to this file'
    )
    argparser.add_argument('--output-markdown', action='store_true',
        help='Reconstruct a Markdown document from the entries and write it to stdout'
    )
    argparser.add_argument('--output-html', action='store_true',
        help='Construct an HTML5 article element from the entries and write it to stdout'
    )
    argparser.add_argument('--output-html-snippet', action='store_true',
        help='Construct a snippet of HTML from the entries and write it to stdout'
    )

    argparser.add_argument('--rewrite-markdown', action='store_true',
        help='Rewrite all input Markdown documents in-place. Note!! Destructive!!'
    )

    argparser.add_argument('--input-refdex', metavar='FILENAME', type=str,
        help='Load this JSON file as the reference-style links index before processing'
    )
    argparser.add_argument('--output-refdex', action='store_true',
        help='Construct reference-style links index from the entries and write it to stdout as JSON'
    )

    argparser.add_argument('--limit', metavar='COUNT', type=int, default=None,
        help='Process no more than this many entries when making an Atom or HTML feed'
    )

    options = argparser.parse_args(sys.argv[1:])

    documents = []

    ### helpers

    def read_document_from(filename):
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
        parser = Parser(markdown_text)
        document = parser.parse_document()
        document.filename = filename
        return document

    def write(s):
        print(s.encode('utf-8'))

    ### input

    for filename in options.input_files:
        document = read_document_from(filename)
        documents.append(document)

    refdex = {}
    if options.input_refdex:
        with codecs.open(options.input_refdex, 'r', encoding='utf-8') as f:
            refdex = json.loads(f.read())

    ### processing

    if options.check_links or options.archive_links_to is not None:
        from feedmark.checkers import archive_links
        result = archive_links(documents, options.archive_links_to)
        write(json.dumps(result, indent=4, sort_keys=True))

    schema = None
    if options.check_against_schema is not None:
        from feedmark.checkers import Schema
        schema_document = read_document_from(options.check_against_schema)
        schema = Schema(schema_document)
        results = []
        for document in documents:
            for section in document.sections:
                result = schema.check(section)
                if result:
                    results.append({
                        'section': section.title,
                        'document': document.title,
                        'result': result
                    })
        if results:
            write(json.dumps(results, indent=4, sort_keys=True))
            sys.exit(1)

    ### processing: collect refdex phase

    for document in documents:
        for section in document.sections:
            refdex[section.title] = {
                'filename': document.filename,
                'anchor': section.anchor
            }

    ### processing: rewrite references phase

    if refdex:
        # TODO: this is not correct.  it is mainly a reminder.
        reference = {}
        for document in documents:
            for (name, url) in document.reference_links:
                reference[name] = url
            for section in document.sections:
                for (name, url) in section.reference_links:
                    reference[name] = url

    ### output

    if options.output_refdex:
        write(json.dumps(refdex, indent=4, sort_keys=True))

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
                    by_property.setdefault(key, {}).setdefault(section.title, value)
        write(json.dumps(by_property, indent=4))

    if options.output_markdown:
        from feedmark.htmlizer import feedmark_markdownize
        for document in documents:
            s = feedmark_markdownize(document, schema=schema)
            write(s)

    if options.rewrite_markdown:
        from feedmark.htmlizer import feedmark_markdownize
        for document in documents:
            s = feedmark_markdownize(document, schema=schema)
            with open(document.filename, 'w') as f:
                f.write(s.encode('UTF-8'))

    if options.output_html:
        from feedmark.htmlizer import feedmark_htmlize
        for document in documents:
            s = feedmark_htmlize(document, schema=schema)
            write(s)

    if options.output_html_snippet:
        from feedmark.htmlizer import feedmark_htmlize_snippet
        s = feedmark_htmlize_snippet(documents, limit=options.limit)
        write(s)

    if options.output_atom:
        feedmark_atomize(documents, options.output_atom, limit=options.limit)


if __name__ == '__main__':
    main(sys.argv[1:])

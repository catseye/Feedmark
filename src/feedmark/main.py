from argparse import ArgumentParser
import codecs
import json
import re
import sys
import urllib

from feedmark.feeds import extract_sections
from feedmark.parser import Parser


def read_document_from(filename):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    parser = Parser(markdown_text)
    document = parser.parse_document()
    document.filename = filename
    return document


def main(args):
    argparser = ArgumentParser()

    argparser.add_argument('input_files', nargs='+', metavar='FILENAME', type=str,
        help='Markdown files containing the embedded entries'
    )

    argparser.add_argument('--by-property', action='store_true',
        help='Output JSON containing a list of all properties found and the entries they were found on'
    )
    argparser.add_argument('--dump-entries', action='store_true',
        help='Output indented summary of the entries on standard output'
    )
    argparser.add_argument('--output-json', action='store_true',
        help='Output JSON containing entries on standard output'
    )

    argparser.add_argument('--output-links', action='store_true',
        help='Output JSON containing all web links extracted from the entries'
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
    argparser.add_argument('--check-for-nodes', action='store_true',
        help='Check if entries contain any Chrysoberyl-style links to nodes'
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
    argparser.add_argument('--output-toc', action='store_true',
        help='Construct a Markdown Table of Contents from the entries and write it to stdout'
    )
    argparser.add_argument('--include-section-count', action='store_true',
        help='When creating a ToC, display the count of contained sections alongside each document'
    )

    argparser.add_argument('--rewrite-markdown', action='store_true',
        help='Rewrite all input Markdown documents in-place. Note!! Destructive!!'
    )

    argparser.add_argument('--input-refdex', metavar='FILENAME', type=str,
        help='Load this JSON file as the reference-style links index before processing'
    )
    argparser.add_argument('--input-refdexes', metavar='FILENAME', type=str,
        help='Load these JSON files as the reference-style links index before processing'
    )
    argparser.add_argument('--output-refdex', action='store_true',
        help='Construct reference-style links index from the entries and write it to stdout as JSON'
    )
    argparser.add_argument('--input-refdex-filename-prefix', type=str, default=None,
        help='After loading refdexes, prepend this to filename of each refdex'
    )

    argparser.add_argument('--limit', metavar='COUNT', type=int, default=None,
        help='Process no more than this many entries when making an Atom or HTML feed'
    )

    options = argparser.parse_args(sys.argv[1:])

    documents = []

    ### helpers

    def write(s):
        print(s.encode('utf-8'))

    ### input

    for filename in options.input_files:
        document = read_document_from(filename)
        documents.append(document)

    refdex = {}
    input_refdexes = []
    if options.input_refdex:
        input_refdexes.append(options.input_refdex)
    if options.input_refdexes:
        for input_refdex in options.input_refdexes.split(','):
            input_refdexes.append(input_refdex.strip())

    for input_refdex in input_refdexes:
        with codecs.open(input_refdex, 'r', encoding='utf-8') as f:
            local_refdex = json.loads(f.read())
            if options.input_refdex_filename_prefix:
                for key, value in local_refdex.iteritems():
                    if 'filename' in value:
                        value['filename'] = options.input_refdex_filename_prefix + value['filename']
            refdex.update(local_refdex)

    ### processing

    if options.check_for_nodes:
        from feedmark.checkers import check_for_nodes
        result = check_for_nodes(documents)
        if result:
            write(json.dumps(result, indent=4, sort_keys=True))
            sys.exit(1)

    if options.check_links or options.archive_links_to is not None:
        from feedmark.checkers import archive_links
        result = archive_links(documents, options.archive_links_to)
        write(json.dumps(result, indent=4, sort_keys=True))

    schema = None
    if options.check_against_schema is not None:
        from feedmark.checkers import Schema
        schema_document = read_document_from(options.check_against_schema)
        schema = Schema(schema_document)
        results = schema.check_documents([document])
        if results:
            write(json.dumps(results, indent=4, sort_keys=True))
            sys.exit(1)

    ### processing: collect refdex phase
    # NOTE: we only run this if we were asked to output a refdex -
    # this is to prevent scurrilous insertion of refdex entries when rewriting.

    if options.output_refdex:
        for document in documents:
            for section in document.sections:
                refdex[section.title] = {
                    'filename': document.filename,
                    'anchor': section.anchor
                }

    ### processing: rewrite references phase

    def rewrite_reference_links(refdex, reference_links):
        from urllib import quote

        new_reference_links = []
        for (name, url) in reference_links:
            if name in refdex:
                entry = refdex[name]
                if 'filename' in entry and 'anchor' in entry:
                    url = '{}#{}'.format(quote(entry['filename']), quote(entry['anchor']))
                elif 'url' in entry:
                    url = entry['url']
                else:
                    raise ValueError("Badly formed refdex entry: {}".format(json.dumps(entry)))
            new_reference_links.append((name, url))
        return new_reference_links

    if refdex:
        for document in documents:
            document.reference_links = rewrite_reference_links(refdex, document.reference_links)
            for section in document.sections:
                section.reference_links = rewrite_reference_links(refdex, section.reference_links)

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

    if options.output_json:
        output_json = {}
        for document in documents:
            document_json = {
                'title': document.title,
                'properties': document.properties,
            }
            for section in document.sections:
                section_json = {
                    'title': section.title,
                    'images': section.images,
                    'properties': section.properties,
                }
                document_json[section.title] = section_json
            output_json[document.title] = document_json
        write(json.dumps(output_json, indent=4, sort_keys=True))

    if options.by_property:
        by_property = {}
        for document in documents:
            for section in document.sections:
                for key, value in section.properties.iteritems():
                    if isinstance(value, list):
                        key = u'{}@'.format(key)
                    by_property.setdefault(key, {}).setdefault(section.title, value)
        write(json.dumps(by_property, indent=4))

    if options.output_links:
        from feedmark.checkers import extract_links_from_documents
        links = extract_links_from_documents(documents)
        jsonable_links = [(url, section.title) for (url, section) in links]
        write(json.dumps(jsonable_links, indent=4, sort_keys=True))

    if options.output_markdown:
        from feedmark.formats.markdown import feedmark_markdownize
        for document in documents:
            s = feedmark_markdownize(document, schema=schema)
            write(s)

    if options.rewrite_markdown:
        from feedmark.formats.markdown import feedmark_markdownize
        for document in documents:
            s = feedmark_markdownize(document, schema=schema)
            with open(document.filename, 'w') as f:
                f.write(s.encode('UTF-8'))

    if options.output_html:
        from feedmark.formats.markdown import feedmark_htmlize
        for document in documents:
            s = feedmark_htmlize(document, schema=schema)
            write(s)

    if options.output_html_snippet:
        from feedmark.formats.markdown import feedmark_htmlize_snippet
        s = feedmark_htmlize_snippet(documents, limit=options.limit)
        write(s)

    if options.output_toc:
        for document in documents:
            filename = document.filename
            if ' ' in filename:
                filename = urllib.quote(filename)

            signs = []
            section_count = len(document.sections)
            if options.include_section_count and section_count > 1:
                signs.append('({})'.format(section_count))

            if document.properties.get('status') == 'under construction':
                signs.append('*(U)*')
            elif document.properties.get('publication-date'):
                pubdate = document.properties['publication-date']
                match = re.search(r'(\w+\s+\d\d\d\d)', pubdate)
                if match:
                    pubdate = match.group(1)
                signs.append('({})'.format(pubdate))

            line = "*   [{}]({}) {}".format(document.title, filename, ' '.join(signs))
            write(line)

    if options.output_atom:
        from feedmark.formats.atom import feedmark_atomize
        feedmark_atomize(documents, options.output_atom, limit=options.limit)


if __name__ == '__main__':
    main(sys.argv[1:])

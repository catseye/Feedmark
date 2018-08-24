from argparse import ArgumentParser
import codecs
import json
import re
import sys

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
    argparser.add_argument('--by-publication-date', action='store_true',
        help='Output JSON list of the embdedded entries, sorted by publication date'
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
        try:
            with codecs.open(input_refdex, 'r', encoding='utf-8') as f:
                local_refdex = json.loads(f.read())
                if options.input_refdex_filename_prefix:
                    for key, value in local_refdex.iteritems():
                        if 'filename' in value:
                            value['filename'] = options.input_refdex_filename_prefix + value['filename']
                refdex.update(local_refdex)
        except:
            sys.stderr.write("Could not read refdex JSON from '{}'\n".format(input_refdex))
            raise

    for key, value in refdex.iteritems():
        try:
            assert isinstance(key, unicode)
            if 'url' in value:
                assert len(value) == 1
                assert isinstance(value['url'], unicode)
                value['url'].encode('utf-8')
            elif 'filename' in value and 'anchor' in value:
                assert len(value) == 2
                assert isinstance(value['filename'], unicode)
                value['filename'].encode('utf-8')
                assert isinstance(value['anchor'], unicode)
                value['anchor'].encode('utf-8')
            else:
                raise NotImplementedError("badly formed refdex")
        except:
            sys.stderr.write("Component of refdex not suitable: '{}: {}'\n".format(repr(key), repr(value)))
            raise

    ### processing

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
        seen_names = set()
        for (name, url) in reference_links:
            if name in seen_names:
                continue
            seen_names.add(name)
            if name in refdex:
                entry = refdex[name]
                if 'filename' in entry and 'anchor' in entry:
                    try:
                        filename = quote(entry['filename'].encode('utf-8'))
                        anchor = quote(entry['anchor'].encode('utf-8'))
                    except:
                        sys.stderr.write(repr(entry))
                        raise
                    url = u'{}#{}'.format(filename, anchor)
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
        output_json = {
            'documents': []
        }
        for document in documents:
            document_json = {
                'filename': document.filename,
                'title': document.title,
                'properties': document.properties,
                'preamble': document.preamble,
                'sections': [],
            }
            for section in document.sections:
                document_json['sections'].append({
                    'title': section.title,
                    'images': section.images,
                    'properties': section.properties,
                    'body': section.body,
                })
            output_json['documents'].append(document_json)
        write(json.dumps(output_json, indent=4, sort_keys=True))

    if options.by_publication_date:
        from feedmark.feeds import construct_entry_url

        items = []
        for document in documents:
            for section in document.sections:
                section_json = {
                    'title': section.title,
                    'images': section.images,
                    'properties': section.properties,
                    'body': section.body,
                    'url': construct_entry_url(section)
                }
                items.append((section.publication_date, section_json))
        items.sort(reverse=True)
        if options.limit:
            items = items[:options.limit]
        output_json = [item for (d, item) in items]
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
        jsonable_links = [(url, section.title if section else "(no section)") for (url, section) in links]
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

    if options.output_atom:
        from feedmark.formats.atom import feedmark_atomize
        feedmark_atomize(documents, options.output_atom, limit=options.limit)


if __name__ == '__main__':
    main(sys.argv[1:])

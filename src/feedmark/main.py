from argparse import ArgumentParser
import json
import sys

from feedmark.loader import (
    read_document_from, read_refdex_from, convert_refdex_to_single_filename_refdex,
)
from feedmark.utils import items


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
    argparser.add_argument('--htmlized-json', action='store_true',
        help='When outputting JSON, convert Markdown fields (preamble, section bodies, etc) to HTML5'
    )
    argparser.add_argument('--ordered-json', action='store_true',
        help='When outputting JSON, generate properties as lists that preserve the order '
             'from the source Feedmark document, instead of as unordered objects'
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
    argparser.add_argument('--input-refdex-filename-prefix', type=str, default=None,
        help='After loading refdexes, prepend this to filename of each refdex'
    )
    argparser.add_argument('--output-refdex', action='store_true',
        help='Construct reference-style links index from the entries and write it to stdout as JSON'
    )
    argparser.add_argument('--output-refdex-single-filename', action='store_true',
        help='When outputting a refdex, ensure that only entries with a single filename are '
             'output, by stripping all but the last filename from multiple filenames entries.'
    )

    argparser.add_argument('--limit', metavar='COUNT', type=int, default=None,
        help='Process no more than this many entries when making an Atom or HTML feed'
    )

    argparser.add_argument('--version', action='version', version="%(prog)s 0.12")

    options = argparser.parse_args(args)

    documents = []

    ### input

    for filename in options.input_files:
        document = read_document_from(filename)
        documents.append(document)

    ### input: load input refdexes

    input_refdexes = []
    if options.input_refdex:
        input_refdexes.append(options.input_refdex)
    if options.input_refdexes:
        for input_refdex in options.input_refdexes.split(','):
            input_refdexes.append(input_refdex.strip())

    refdex = read_refdex_from(input_refdexes, input_refdex_filename_prefix=options.input_refdex_filename_prefix)

    ### processing

    schema = None
    if options.check_against_schema is not None:
        from feedmark.checkers import Schema
        schema_document = read_document_from(options.check_against_schema)
        schema = Schema(schema_document)
        results = schema.check_documents([document])
        if results:
            sys.stdout.write(json.dumps(results, indent=4, sort_keys=True))
            sys.exit(1)

    ### processing: collect refdex phase
    # NOTE: we only run this if we were asked to output a refdex -
    # this is to prevent scurrilous insertion of refdex entries when rewriting.

    if options.output_refdex:
        for document in documents:
            for section in document.sections:
                if section.title in refdex:
                    entry = refdex[section.title]
                    if entry['anchor'] != section.anchor:
                        raise ValueError("Inconsistent anchors: {} in refex, {} in document".format(entry['anchor'], section.anchor))
                    if 'filename' in entry:
                        entry['filenames'] = []
                        del entry['filename']
                    entry['filenames'].append(document.filename)
                else:
                    refdex[section.title] = {
                        'filenames': [document.filename],
                        'anchor': section.anchor
                    }

    ### processing: rewrite references phase

    if refdex:
        for document in documents:
            document.rewrite_reference_links(refdex)

    ### output

    if options.output_refdex:
        if options.output_refdex_single_filename:
            refdex = convert_refdex_to_single_filename_refdex(refdex)
        sys.stdout.write(json.dumps(refdex, indent=4, sort_keys=True))

    if options.dump_entries:
        for document in documents:
            for section in document.sections:
                print(section.title)
                for (name, url) in section.images:
                    print(u'    !{}: {}'.format(name, url))
                for key, value in items(section.properties):
                    if isinstance(value, list):
                        print(u'    {}@'.format(key))
                        for subitem in value:
                            print(u'        {}'.format(subitem))
                    else:
                        print(u'    {}: {}'.format(key, value))

    if options.output_json:
        json_options = {
            'htmlize': options.htmlized_json,
            'ordered': options.ordered_json,
        }
        output_json = {
            'documents': [d.to_json_data(**json_options) for d in documents]
        }
        sys.stdout.write(json.dumps(output_json, indent=4, sort_keys=True))

    if options.by_publication_date:
        from feedmark.feeds import construct_entry_url

        dated_items = []
        for document in documents:
            for section in document.sections:
                section_json = {
                    'title': section.title,
                    'images': section.images,
                    'properties': section.properties,
                    'body': section.body,
                    'url': construct_entry_url(section)
                }
                dated_items.append((section.publication_date, section_json))
        dated_items.sort(reverse=True)
        if options.limit:
            dated_items = dated_items[:options.limit]
        output_json = [item for (d, item) in dated_items]
        sys.stdout.write(json.dumps(output_json, indent=4, sort_keys=True))

    if options.by_property:
        by_property = {}
        for document in documents:
            for section in document.sections:
                for key, value in items(section.properties):
                    if isinstance(value, list):
                        key = u'{}@'.format(key)
                    by_property.setdefault(key, {}).setdefault(section.title, value)
        sys.stdout.write(json.dumps(by_property, indent=4))

    if options.output_links:
        from feedmark.checkers import extract_links_from_documents
        links = extract_links_from_documents(documents)
        sys.stdout.write(json.dumps(links, indent=4, sort_keys=True))

    if options.output_markdown:
        from feedmark.formats.markdown import feedmark_markdownize
        for document in documents:
            s = feedmark_markdownize(document, schema=schema)
            sys.stdout.write(s)

    if options.rewrite_markdown:
        from feedmark.formats.markdown import feedmark_markdownize
        for document in documents:
            s = feedmark_markdownize(document, schema=schema)
            with open(document.filename, 'w') as f:
                f.write(s)

    if options.output_html:
        from feedmark.formats.markdown import feedmark_htmlize
        for document in documents:
            s = feedmark_htmlize(document, schema=schema)
            sys.stdout.write(s)

    if options.output_atom:
        from feedmark.formats.atom import feedmark_atomize
        feedmark_atomize(documents, options.output_atom, limit=options.limit)


if __name__ == '__main__':
    main(sys.argv[1:])

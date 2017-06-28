from argparse import ArgumentParser
import codecs
from datetime import datetime
import sys

import atomize
import markdown

from feedmark.parser import Parser


def feedmark(in_filename, out_filename):
    with codecs.open(in_filename, 'r', encoding='utf-8') as f:
        in_doc = f.read()

    parser = Parser(in_doc)
    document = parser.parse_document()

    author = document.properties['author']
    url = document.properties['url']

    entries = []
    for section in document.sections:
        guid = url + "/" + section.title
        updated = section.publication_date

        summary = atomize.Summary(markdown.markdown(section.body), content_type='html')

        #links = [atomize.Link(section.link, content_type='text/html',
        #                      rel='alternate')]
        links = []
        entry = atomize.Entry(title=section.title, guid=guid, updated=updated,
                              summary=summary, links=links)
        entries.append(entry)

    limit = None
    if limit and len(entries) > limit:
        entries = entries[:limit]

    kwargs = dict(
        title=document.title,
        updated=datetime.utcnow(),
        guid=url,
        entries=entries
    )

    if author is not None:
        kwargs['author'] = author

    if url is not None:
        kwargs['self_link'] = url

    feed = atomize.Feed(**kwargs)

    feed.write_file(out_filename)


def main(args):
    argparser = ArgumentParser()

    argparser.add_argument('infile', metavar='FILENAME', type=str,
        help='A Markdown file containing the feed.'
    )
    argparser.add_argument('outfile', metavar='FILENAME', type=str)

    options = argparser.parse_args(sys.argv[1:])

    return feedmark(options.infile, options.outfile)


if __name__ == '__main__':
    main(sys.argv[1:])

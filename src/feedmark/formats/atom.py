from __future__ import absolute_import

from datetime import datetime

import atomize

from feedmark.feeds import extract_feed_properties, extract_sections, construct_entry_url
from feedmark.formats.markdown import markdown_to_html5


def convert_section_to_entry(section, properties, markdown_links_base=None):

    guid = properties['url'] + "/" + section.title
    updated = section.publication_date

    summary = atomize.Summary(markdown_to_html5(section.body), content_type='html')

    links = []
    entry_url = construct_entry_url(section)
    if entry_url is not None:
        links.append(atomize.Link(entry_url, content_type='text/html', rel='alternate'))

    return atomize.Entry(
        title=section.title,
        guid=guid,
        updated=updated,
        summary=summary,
        links=links
    )


def feedmark_atomize(documents, out_filename, limit=None):
    properties = {}

    for document in documents:
        these_properties = extract_feed_properties(document)
        properties.update(these_properties)  # TODO: something more elegant than this

    entries = []
    for section in extract_sections(documents):
        entries.append(convert_section_to_entry(section, properties))

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

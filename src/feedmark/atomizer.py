from datetime import datetime

import atomize
import markdown


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

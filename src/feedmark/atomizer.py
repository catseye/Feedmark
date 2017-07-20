from datetime import datetime

import atomize
import markdown


def extract_feed_entries(document, markdown_links_base=None):
    properties = {}

    properties['title'] = document.title
    properties['author'] = document.properties['author']
    properties['url'] = document.properties['url']

    entries = []
    for section in document.sections:
        guid = properties['url'] + "/" + section.title
        updated = section.publication_date

        summary = atomize.Summary(markdown.markdown(section.body), content_type='html')

        links = []
        if markdown_links_base is not None:
            section_anchor = section.title.replace("'", '').replace(":", '').replace(' ', '-').lower()
            links.append(
                atomize.Link(
                    '{}#{}'.format(markdown_links_base, section_anchor),
                    content_type='text/html',
                    rel='alternate'
                )
            )

        entry = atomize.Entry(title=section.title, guid=guid, updated=updated,
                              summary=summary, links=links)
        entries.append(entry)

    return entries, properties


def feedmark_atomize(documents, out_filename, limit=None):
    entries = []
    properties = {}

    for document in documents:
        # FIXME don't hardcode this links base thing
        these_entries, these_properties = extract_feed_entries(document, markdown_links_base='https://github.com/catseye/Feedmark/blob/master/eg/Recent%20Llama%20Sightings.md')
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

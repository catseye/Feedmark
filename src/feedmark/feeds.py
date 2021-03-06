# Feed-related, but Atom-independent, functions.

from feedmark.utils import quote_plus


def construct_entry_url(section):
    # Currently supports links to anchors generated by Github's Markdown renderer.

    if 'link-target-url' not in section.document.properties:
        return None

    return '{}#{}'.format(section.document.properties['link-target-url'], quote_plus(section.anchor))


def extract_feed_properties(document):
    properties = {}
    properties['title'] = document.title
    properties['author'] = document.properties['author']
    properties['url'] = document.properties['url']
    properties['link-target-url'] = document.properties.get('link-target-url')
    return properties


def extract_sections(documents):
    sections = []
    for document in documents:
        for section in document.sections:
            sections.append(section)
    sections.sort(key=lambda section: section.publication_date, reverse=True)
    return sections

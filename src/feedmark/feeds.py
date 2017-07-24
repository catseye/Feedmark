# Feed-related, but Atom-independent, functions.


def extract_feed_properties(document):
    properties = {}
    properties['title'] = document.title
    properties['author'] = document.properties['author']
    properties['url'] = document.properties['url']
    properties['link-to-anchors-on'] = document.properties.get('link-to-anchors-on')
    return properties


def extract_sections(documents):
    sections = []
    for document in documents:
        for section in document.sections:
            section.document = document  # TODO: maybe the parser should do this for us
            sections.append(section)
    sections.sort(key=lambda section: section.publication_date, reverse=True)
    return sections

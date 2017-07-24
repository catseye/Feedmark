from datetime import datetime

import markdown

from feedmark.feeds import extract_sections


def render_section(section):
    date = section.publication_date.strftime('%b %-d, %Y')
    if 'summary' in section.properties:
        summary = markdown.markdown(section.properties['summary'])
    else:
        # TODO: link
        summary = section.title
    return '{}: {}'.format(date, summary)


def feedmark_htmlize(documents, limit=None):
    properties = {}

    sections = extract_sections(documents)
    s = ''
    s += u'<ul>'
    for (n, section) in enumerate(sections):
        if limit is not None and n >= limit:
            break
        s += u'<li>{}</li>\n'.format(render_section(section))
    s += u'</ul>'

    return s

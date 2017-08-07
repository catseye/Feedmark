from datetime import datetime
import re

import markdown

from feedmark.feeds import extract_sections, construct_entry_url


def strip_outer_p(text):
    match = re.match(r'^\s*\<p\>\s*(.*?)\s*\<\/p\>\s*$', text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def render_section_snippet(section):
    date = section.publication_date.strftime('%b %-d, %Y')
    if 'summary' in section.properties:
        summary = strip_outer_p(markdown.markdown(section.properties['summary']))
    else:
        summary = section.title
    url = construct_entry_url(section)
    read_more = ''
    if url is not None:
        read_more = '<a href="{}">Read more...</a>'.format(url)
    return '{}: {} {}'.format(date, summary, read_more)


def feedmark_htmlize_snippet(documents, limit=None):
    properties = {}

    sections = extract_sections(documents)
    s = ''
    s += u'<ul>'
    for (n, section) in enumerate(sections):
        if limit is not None and n >= limit:
            break
        s += u'<li>{}</li>\n'.format(render_section_snippet(section))
    s += u'</ul>'

    return s


def feedmark_markdownize(document):
    md = u'# ' + document.title + u'\n\n'
    md += u'\n'.join(document.preamble) + u'\n\n'
    for section in document.sections:
        md += u'\n'
        md += u'### {}\n\n'.format(section.title)
        for key, value in section.properties.iteritems():
            md += u'*   {}: {}\n'.format(key, value)
        md += u'\n'
        md += section.body
    return md


def feedmark_htmlize(document):
    return markdown.markdown(feemark_markdownize(document))

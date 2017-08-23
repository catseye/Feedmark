from __future__ import absolute_import

from datetime import datetime
import re

from markdown import markdown

from feedmark.feeds import extract_sections, construct_entry_url


def strip_outer_p(text):
    match = re.match(r'^\s*\<p\>\s*(.*?)\s*\<\/p\>\s*$', text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def render_section_snippet(section):
    date = section.publication_date.strftime('%b %-d, %Y')
    if 'summary' in section.properties:
        summary = strip_outer_p(markdown(section.properties['summary']))
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


def items_in_priority_order(di, priority):
    for key in priority:
        if key in di:
            yield key, di[key]
    for key, item in sorted(di.iteritems()):
        if key not in priority:
            yield key, item


def markdownize_properties(properties, property_priority_order):
    if not properties:
        return ''
    md = ''
    for key, value in items_in_priority_order(properties, property_priority_order):
        if isinstance(value, list):
            for subitem in value:
                md += u'*   {} @ {}\n'.format(key, subitem)
        else:
            md += u'*   {}: {}\n'.format(key, value)
    md += '\n'
    return md


def markdownize_reference_links(reference_links):
    if not reference_links:
        return ''
    md = ''
    md += '\n'
    for name, url in reference_links:
        md += '[{}]: {}\n'.format(name, url)
    return md


def feedmark_markdownize(document, schema=None):
    property_priority_order = []
    if schema is not None:
        property_priority_order = schema.get_property_priority_order()

    md = u'{}\n{}\n\n'.format(document.title, '=' * len(document.title))
    md += markdownize_properties(document.properties, property_priority_order)
    md += u'\n'.join(document.preamble)
    md += markdownize_reference_links(document.reference_links)
    for section in document.sections:
        md += u'\n'
        md += u'### {}\n\n'.format(section.title)
        if section.images:
            for name, url in section.images:
                md += u'![{}]({})\n'.format(name, url)
            md += u'\n'
        md += markdownize_properties(section.properties, property_priority_order)
        md += section.body
        md += markdownize_reference_links(section.reference_links)
    md += '\n'
    return md


def feedmark_htmlize(document, *args, **kwargs):
    return markdown(feedmark_markdownize(document, *args, **kwargs))

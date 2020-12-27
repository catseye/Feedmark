from __future__ import absolute_import

from collections import OrderedDict
import re

from feedmark.utils import items_in_priority_order, unicode


def remove_outer_p(html):
    match = re.match(r'^\s*\<\s*p\s*\>\s*(.*?)\s*\<\s*/\s*p\s*\>\s*$', html)
    if match:
        html = match.group(1)
    return html


def markdown_to_html5(text, reference_links=None):
    """Canonical function used within `feedmark` to convert Markdown text to a HTML5 snippet."""
    from markdown import markdown

    if reference_links:
        text += markdownize_reference_links(reference_links)

    return markdown(text, extensions=['markdown.extensions.toc'])


def markdown_to_html5_deep(obj, **kwargs):
    if obj is None:
        return None
    elif isinstance(obj, OrderedDict):
        return OrderedDict((k, markdown_to_html5_deep(v, **kwargs)) for k, v in obj.items())
    elif isinstance(obj, dict):
        return dict((k, markdown_to_html5_deep(v, **kwargs)) for k, v in obj.items())
    elif isinstance(obj, list):
        return [markdown_to_html5_deep(subobj, **kwargs) for subobj in obj]
    else:
        return remove_outer_p(markdown_to_html5(unicode(obj), **kwargs))


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
        return u''
    md = u''
    md += u'\n'
    for name, url in reference_links:
        md += u'[{}]: {}\n'.format(name, url)
    return md


def feedmark_markdownize(document, schema=None):
    property_priority_order = []
    if schema is not None:
        property_priority_order = schema.get_property_priority_order()

    md = u'{}\n{}\n\n'.format(document.title, '=' * len(document.title))
    md += markdownize_properties(document.properties, property_priority_order)
    md += document.preamble
    md += markdownize_reference_links(document.reference_links)
    for section in document.sections:
        md += u'\n'
        md += u'### {}\n\n'.format(section.title)
        if section.images:
            for entry in section.images:
                if 'link' in entry:
                    md += u'[![{}]({})]({})\n'.format(
                        entry['description'], entry['source'], entry['link'],
                    )
                else:
                    md += u'![{}]({})\n'.format(
                        entry['description'], entry['source'],
                    )
            md += u'\n'
        md += markdownize_properties(section.properties, property_priority_order)
        md += section.body
        md += markdownize_reference_links(section.reference_links)
    md += '\n'
    return md


def feedmark_htmlize(document, *args, **kwargs):
    return markdown_to_html5(feedmark_markdownize(document, *args, **kwargs))

from __future__ import absolute_import

from datetime import datetime
import re

from markdown import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

from feedmark.parser import anchor_for


class AnchorBestower(Treeprocessor):
    def run(self, root):
        self.rewrite(root)

    def rewrite(self, element):
        if element.tag == 'h3':
            element.set('id', anchor_for(element.text).decode('utf-8'))
        else:
            for child in element:
                self.rewrite(child)


class AnchorExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add('bestow-anchors', AnchorBestower(), '>inline')


anchor_extension = AnchorExtension()


def markdown_to_html5(text):
    """Canonical function used within `feedmark` to convert Markdown text to a HTML5 snippet."""
    return markdown(text, extensions=[anchor_extension])


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
            for name, url in section.images:
                md += u'![{}]({})\n'.format(name, url)
            md += u'\n'
        md += markdownize_properties(section.properties, property_priority_order)
        md += section.body
        md += markdownize_reference_links(section.reference_links)
    md += '\n'
    return md


def feedmark_htmlize(document, *args, **kwargs):
    return markdown_to_html5(feedmark_markdownize(document, *args, **kwargs))

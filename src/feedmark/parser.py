#!/usr/bin/env python
# encoding: UTF-8

from datetime import datetime
from collections import OrderedDict
import re

from feedmark.formats.markdown import markdown_to_html5, markdown_to_html5_deep
from feedmark.utils import quote


def rewrite_reference_links(refdex, reference_links):
    new_reference_links = []
    seen_names = set()
    for (name, url) in reference_links:
        if name in seen_names:
            continue
        seen_names.add(name)
        if name in refdex:
            entry = refdex[name]
            if 'filename' in entry and 'anchor' in entry:
                filename = quote(entry['filename'].encode('utf-8'))
                anchor = quote(entry['anchor'].encode('utf-8'))
                url = u'{}#{}'.format(filename, anchor)
            elif 'filenames' in entry and 'anchor' in entry:
                # pick the last one, for compatibility with single-refdex style
                filename = quote(entry['filenames'][-1].encode('utf-8'))
                anchor = quote(entry['anchor'].encode('utf-8'))
                url = u'{}#{}'.format(filename, anchor)
            elif 'url' in entry:
                url = entry['url']
            else:
                raise ValueError("Badly formed refdex entry: {}".format(entry))
        new_reference_links.append((name, url))
    return new_reference_links


class Document(object):
    def __init__(self, title):
        self.title = title
        self.properties = OrderedDict()

        self.preamble = None
        self.sections = []

    def __str__(self):
        return "document '{}'".format(self.title.encode('utf-8'))

    def rewrite_reference_links(self, refdex):
        self.reference_links = rewrite_reference_links(refdex, self.reference_links)
        for section in self.sections:
            section.reference_links = rewrite_reference_links(refdex, section.reference_links)

    def global_reference_links(self):
        reference_links = []
        reference_links.extend(self.reference_links)
        for section in self.sections:
            reference_links.extend(section.reference_links)
        return reference_links

    def to_json_data(self, **kwargs):

        if kwargs.get('htmlize', False):
            if 'reference_links' not in kwargs:
                kwargs['reference_links'] = self.global_reference_links()
            preamble = markdown_to_html5(self.preamble, reference_links=kwargs['reference_links'])
            properties = markdown_to_html5_deep(self.properties, reference_links=kwargs['reference_links'])
        else:
            preamble = self.preamble
            properties = self.properties

        if kwargs.get('ordered', False):
            properties_list = []
            for key, value in properties.items():
                properties_list.append([key, value])
            properties = properties_list
        else:
            properties = dict(properties)

        return {
            'filename': self.filename,
            'title': self.title,
            'properties': properties,
            'preamble': preamble,
            'sections': [s.to_json_data(**kwargs) for s in self.sections],
        }


class Section(object):
    def __init__(self, title):
        self.document = None
        self.title = title
        self.properties = OrderedDict()

        self.lines = []

    def __str__(self):
        s = "section '{}'".format(self.title.encode('utf-8'))
        if self.document:
            s += " of " + str(self.document)
        return s

    @property
    def body(self):
        return '\n'.join(self.lines)

    @property
    def publication_date(self):
        formats = (
            "%b %d %Y %H:%M:%S",
            "%a, %d %b %Y %H:%M:%S GMT",
        )
        for format in formats:
            try:
                return datetime.strptime(self.properties['date'], format)
            except KeyError:
                raise KeyError("could not find 'date' on {}".format(self))
            except ValueError:
                pass
        raise NotImplementedError

    @property
    def anchor(self):
        from markdown.extensions.toc import slugify

        return slugify(self.title, '-')

    def to_json_data(self, **kwargs):

        if kwargs.get('htmlize', False):
            body = markdown_to_html5(self.body, reference_links=kwargs['reference_links'])
            properties = markdown_to_html5_deep(self.properties, reference_links=kwargs['reference_links'])
        else:
            body = self.body
            properties = self.properties

        if kwargs.get('ordered', False):
            properties_list = []
            for key, value in properties.items():
                properties_list.append([key, value])
            properties = properties_list
        else:
            properties = dict(properties)

        return {
            'title': self.title,
            'anchor': self.anchor,
            'images': self.images,
            'properties': properties,
            'body': body,
        }


class Parser(object):

    def __init__(self, doc):
        self.lines = doc.split('\n')
        self.index = 0
        self.line = self.lines[self.index]
        self.index += 1

    def scan(self):
        self.line = self.lines[self.index]
        self.index += 1

    def eof(self):
        return self.index > len(self.lines) - 1

    def is_blank_line(self):
        return re.match(r'^\s*$', self.line)

    def is_image_line(self):
        return (
            re.match(r'^\!\[.*?\]\(.*?\)\s*$', self.line) or
            re.match(r'^\[\!\[.*?\]\(.*?\)\]\(.*?\)\s*$', self.line)
        )

    def is_property_line(self):
        return re.match(r'^\*\s+(.*?)\s*(\:|\@)\s*(.*?)\s*$', self.line)

    def is_heading_line(self):
        return re.match(r'^\#\#\#\s+(.*?)\s*$', self.line)

    def is_reference_link_line(self):
        return re.match(r'^\[(.*?)\]\:\s*(.*?)\s*$', self.line)

    def parse_document(self):
        # Feed       ::= :Title Properties Body {Section}.
        # Section    ::= {:Blank} :Heading {Image} Properties Body.
        # Properties ::= {:Blank | :Property}.
        # Body       ::= {:NonHeadingLine}.

        title = self.parse_title()
        document = Document(title)
        document.properties = self.parse_properties()
        lines, reference_links = self.parse_body()
        document.preamble = u'\n'.join(lines)
        document.reference_links = reference_links
        while not self.eof():
            section = self.parse_section()
            section.document = document
            document.sections.append(section)
        return document

    def parse_title(self):
        match = re.match(r'^\#\s+(.*?)\s*$', self.line)
        if match:
            title = match.group(1)
            self.scan()
            return title
        match = re.match(r'^\s*(.*?)\s*$', self.line)
        if match:
            title = match.group(1)
            self.scan()
            match = re.match(r'^\s*(\=+)\s*$', self.line)
            if match:
                self.scan()
                return title
        raise ValueError('Expected title')

    def parse_property(self):
        match = re.match(r'^\*\s+(.*?)\s*\@\s*(.*?)\s*$', self.line)
        if match:
            (key, val) = (match.group(1), match.group(2))
            self.scan()
            return ('@', key, val)
        match = re.match(r'^\*\s+(.*?)\s*\:\s*(.*?)\s*$', self.line)
        if match:
            (key, val) = (match.group(1), match.group(2))
            self.scan()
            return (':', key, val)
        raise ValueError('Expected property')

    def parse_properties(self):
        properties = OrderedDict()
        while self.is_blank_line() or self.is_property_line():
            if self.is_property_line():
                kind, key, val = self.parse_property()
                if kind == ':':
                    if key in properties:
                        raise KeyError('{} already given'.format(key))
                    properties[key] = val
                elif kind == '@':
                    properties.setdefault(key, []).append(val)
                else:
                    raise NotImplementedError(kind)
            else:
                self.scan()
        return properties

    def parse_section(self):
        while self.is_blank_line():
            self.scan()

        match = re.match(r'^\#\#\#\s+(.*?)\s*(\#\#\#)?\s*$', self.line)
        if not match:
            raise ValueError('Expected section, found "{}"'.format(self.line))

        section = Section(match.group(1))
        self.scan()
        section.images = self.parse_images()
        section.properties = self.parse_properties()
        lines, reference_links = self.parse_body()
        section.lines = lines
        section.reference_links = reference_links
        return section

    def parse_images(self):
        images = []
        while self.is_blank_line() or self.is_image_line():
            if self.is_image_line():
                match = re.match(r'^\!\[(.*?)\]\((.*?)\)\s*$', self.line)
                if match:
                    images.append({
                        'description': match.group(1),
                        'source': match.group(2),
                    })
                else:
                    match = re.match(r'^\[\!\[(.*?)\]\((.*?)\)\]\((.*?)\)\s*$', self.line)
                    images.append({
                        'description': match.group(1),
                        'source': match.group(2),
                        'link': match.group(3),
                    })
            self.scan()
        return images

    def parse_body(self):
        lines = []
        reference_links = []
        while not self.eof() and not self.is_heading_line() and not self.is_reference_link_line():
            lines.append(self.line)
            self.scan()
        while not self.eof() and (self.is_reference_link_line() or self.is_blank_line()):
            if self.is_reference_link_line():
                match = re.match(r'^\[(.*?)\]\:\s*(.*?)\s*$', self.line)
                if match:
                    reference_links.append((match.group(1), match.group(2)))
            self.scan()
        return (lines, reference_links)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

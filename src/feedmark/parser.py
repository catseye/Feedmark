#!/usr/bin/env python

from datetime import datetime
import re


class Document(object):
    def __init__(self, title):
        self.title = title
        self.properties = {}

        self.sections = []

    def __str__(self):
        return "document '{}'".format(self.title.encode('utf-8'))


class Section(object):
    def __init__(self, title):
        self.document = None
        self.title = title
        self.properties = {}

        self.lines = []

    def __str__(self):
        s = "section '{}'".format(self.title.encode('utf-8'))
        if self.document:
            s += " of " + str(self.document)
        return s

    def add_line(self, line):
        self.lines.append(line.rstrip())

    def set(self, key, value):
        self.properties[key] = value

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
        return re.match(r'^\!\[.*?\]\(.*?\)\s*$', self.line)

    def is_property_line(self):
        return re.match(r'^\*\s+(.*?)\s*(\:|\@)\s*(.*?)\s*$', self.line)

    def is_heading_line(self):
        return re.match(r'^\#.*?$', self.line)

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
        preamble, reference_links = self.parse_body()
        document.preamble = preamble
        document.reference_links = reference_links
        while not self.eof():
            section = self.parse_section()
            section.document = document
            document.sections.append(section)
        return document

    def parse_title(self):
        match = re.match(r'^\#\s*([^#].*?)\s*$', self.line)
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
        properties = {}
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

        match = re.match(r'^\#\#\#\s*([^#].*?)\s*$', self.line)
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
                images.append( (match.group(1), match.group(2),) )
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

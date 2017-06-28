#!/usr/bin/env python

from datetime import datetime
import re


class Document(object):
    def __init__(self, title):
        self.title = title
        self.properties = {}

        self.sections = []


class Section(object):
    def __init__(self, title):
        self.title = title
        self.properties = {}

        self.lines = []

    def __str__(self):
        return "section '{}'".format(self.title.encode('utf-8'))

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

    def is_property_line(self):
        return re.match(r'^\*\s+(.*?)\s*\:\s*(.*?)\s*$', self.line)

    def is_heading_line(self):
        return re.match(r'^\#.*?$', self.line)

    def parse_document(self):
        # Feed       ::= :Title Properties {Section}.
        # Section    ::= {:Blank} :Heading Properties Body.
        # Properties ::= {:Blank | :Property}.
        # Body       ::= {:NonHeadingLine}.

        title = self.parse_title()
        document = Document(title)
        document.properties = self.parse_properties()
        while not self.eof():
            section = self.parse_section()
            document.sections.append(section)
        return document

    def parse_title(self):
        match = re.match(r'^\#\s*([^#].*?)\s*$', self.line)
        if not match:
            raise ValueError('Expected title')
        title = match.group(1)
        self.scan()
        return title

    def parse_property(self):
        match = re.match(r'^\*\s+(.*?)\s*\:\s*(.*?)\s*$', self.line)
        if not match:
            raise ValueError('Expected property')
        (key, val) = (match.group(1), match.group(2))
        self.scan()
        return (key, val)

    def parse_properties(self):
        properties = {}
        while self.is_blank_line() or self.is_property_line():
            if self.is_property_line():
                key, val = self.parse_property()
                if key in properties:
                    raise KeyError('{} already given'.format(key))
                properties[key] = val
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
        section.properties = self.parse_properties()
        section.lines = self.parse_body()

        return section

    def parse_body(self):
        lines = []
        while not self.eof() and not self.is_heading_line():
            lines.append(self.line)
            self.scan()
        return lines

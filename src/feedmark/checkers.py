from __future__ import absolute_import

from feedmark.formats.markdown import markdown_to_html5
from feedmark.utils import items


class Schema(object):
    def __init__(self, document):
        self.document = document
        self.property_rules = {}
        self.property_priority_order = []
        for section in self.document.sections:
            self.property_rules[section.title] = section
            self.property_priority_order.append(section.title)

    def check(self, section):
        results = []
        for key, value in items(section.properties):
            if key not in self.property_rules:
                results.append(['extra', key])
        for key, value in items(self.property_rules):
            optional = value.properties.get('optional', 'false') == 'true'
            if optional:
                continue
            if key not in section.properties:
                results.append(['missing', key])
        return results

    def check_documents(self, documents):
        results = []
        for document in documents:
            for section in document.sections:
                result = self.check(section)
                if result:
                    results.append({
                        'section': section.title,
                        'document': document.title,
                        'result': result
                    })
        return results

    def get_property_priority_order(self):
        return self.property_priority_order


def extract_links(html_text):
    from bs4 import BeautifulSoup

    links = []
    soup = BeautifulSoup(html_text, 'html.parser')
    for link in soup.find_all('a'):
        url = link.get('href')
        links.append(url)

    return links


def extract_links_from_documents(documents):
    links = []

    def make_link(url, section=None, **kwargs):
        link = {
            'url': url,
        }
        if section:
            link.update({
                'section': section.title,
                'document': section.document.title,
            })
        link.update(kwargs)
        return link

    def extend_links(section, md):
        links.extend([make_link(url, section=section) for url in extract_links(markdown_to_html5(md))])

    for document in documents:
        for name, url in document.reference_links:
            links.append(make_link(url, name=name))
        for section in document.sections:
            for (name, url) in section.images:
                links.append(make_link(url, section=section, name=name))
            for key, value in items(section.properties):
                if isinstance(value, list):
                    for subitem in value:
                        extend_links(section, subitem)
                else:
                    extend_links(section, value)
            for name, url in section.reference_links:
                links.append(make_link(url, section=section, name=name))
            extend_links(section, section.body)
    return links

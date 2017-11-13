from __future__ import absolute_import

import hashlib
import os
import re
from time import sleep, localtime, strftime
import urllib

from bs4 import BeautifulSoup
import requests

from feedmark.formats.markdown import markdown_to_html5

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs): return x


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
        for key, value in section.properties.iteritems():
            if key not in self.property_rules:
                results.append(['extra', key])
        for key, value in self.property_rules.iteritems():
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

    links = []
    soup = BeautifulSoup(html_text, 'html.parser')
    for link in soup.find_all('a'):
        url = link.get('href')
        links.append(url)

    return links


def extract_links_from_documents(documents):
    links = []
    for document in documents:
        for name, url in document.reference_links:
            links.append((url, None))
        for section in document.sections:
            for (name, url) in section.images:
                links.append((url, section))
            for key, value in section.properties.iteritems():
                if isinstance(value, list):
                    for subitem in value:
                        links.extend([(url, section) for url in extract_links(markdown_to_html5(subitem))])
                else:
                    links.extend([(url, section) for url in extract_links(markdown_to_html5(value))])
            for name, url in section.reference_links:
                links.append((url, section))
            links.extend([(url, section) for url in extract_links(markdown_to_html5(section.body))])
    return links


def url_to_dirname_and_filename(url):
    parts = url.split('/')
    parts = parts[2:]
    domain_name = parts[0]
    domain_name = urllib.quote_plus(domain_name)
    parts = parts[1:]
    filename = '/'.join(parts)
    filename = urllib.quote_plus(filename)
    if not filename:
        filename = 'index.html'
    return (domain_name, filename)


def compute_hash(filename):
    collector = hashlib.sha1()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            collector.update(data)
    return collector.hexdigest()


def download(url, dirname, filename):
    response = requests.get(url, stream=True)
    partname = os.path.join(dirname, filename + '_part')
    with open(partname, "wb") as f:
        for data in response.iter_content():
            f.write(data)
    destname = os.path.join(dirname, filename)
    if os.path.exists(destname):
        desthash = compute_hash(destname)
        parthash = compute_hash(partname)
        if desthash == parthash:
            os.unlink(partname)
        else:
            mtime = os.path.getmtime(destname)
            timestring = strftime('%Y.%m%d.%H%M%S', localtime(mtime))
            archname = '{}_REV{}'.format(destname, timestring)
            os.rename(destname, archname)
            os.rename(partname, destname)
    else:
        os.rename(partname, destname)
    return response


delay_between_fetches = 0


def archive_links(documents, article_root, dest_dir):
    """If dest_dir is None, links will only be checked for existence, not downloaded."""
    links = extract_links_from_documents(documents)

    failures = []
    for url, section in tqdm(links, total=len(links)):
        try:
            if url.startswith(('#',)):
                continue
            elif not url.startswith(('http://', 'https://')):
                if '#' in url:
                    filename, anchor = url.split('#')
                else:
                    filename, anchor = url, ""
                filename = urllib.unquote(filename)
                filename = os.path.join(article_root, filename)
                if not os.path.exists(filename):
                    raise ValueError('Local file "{}" does not exist'.format(filename))
                continue
            elif dest_dir is not None:
                dirname, filename = url_to_dirname_and_filename(url)
                dirname = os.path.join(dest_dir, dirname)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                response = download(url, dirname, filename)
            else:
                response = requests.head(url)
            status = response.status_code
        except Exception as e:
            status = str(e)
        if status not in (200, 301, 302, 303):
            failures.append({
                'status': status,
                'url': url,
                'section': str(section)
            })
        if delay_between_fetches > 0:
            sleep(delay_between_fetches)
    return failures

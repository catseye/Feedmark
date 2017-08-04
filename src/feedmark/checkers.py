import os
import urllib

from bs4 import BeautifulSoup
import markdown
import requests

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs): return x


def extract_links(html_text):

    links = []
    soup = BeautifulSoup(html_text, 'html.parser')
    for link in soup.find_all('a'):
        url = link.get('href')
        if not url.startswith(('http://', 'https://')):
            print('skipping url', url)
            continue
        links.append(url)

    return links


def extract_links_from_documents(documents):
    links = []
    for document in documents:
        for section in document.sections:
            for (name, url) in section.images:
                links.append((url, section))
            for key, value in section.properties.iteritems():
                if isinstance(value, list):
                    for subitem in value:
                        links.extend([(url, section) for url in extract_links(markdown.markdown(subitem))])
                else:
                    links.extend([(url, section) for url in extract_links(markdown.markdown(value))])
            links.extend([(url, section) for url in extract_links(markdown.markdown(section.body))])
    return links


def url_to_dirname_and_filename(url):
    parts = url.split('/')
    parts = parts[2:]
    domain_name = parts[0]
    domain_name = urllib.quote_plus(domain_name)
    parts = parts[1:]
    filename = '/'.join(parts)
    filename = urllib.quote_plus(filename)
    return (domain_name, filename)


def download(url, filename):
    response = requests.get(url, stream=True)
    part_filename = filename + '_part'
    with open(part_filename, "wb") as f:
        for data in response.iter_content():
            f.write(data)
    os.rename(part_filename, filename)
    return response


def archive_links(documents, dest_dir):
    """If dest_dir is None, links will only be checked for existence, not downloaded."""
    links = extract_links_from_documents(documents)

    failures = []
    for url, section in tqdm(links, total=len(links)):
        try:
            if dest_dir is not None:
                dirname, filename = url_to_dirname_and_filename(url)
                dirname = os.path.join(dest_dir, dirname)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                filename = os.path.join(dirname, filename)
                response = download(url, filename)
            else:
                response = requests.head(url)
            status = response.status_code
        except Exception as e:
            status = str(e)
        if status not in (200, 301, 302, 303):
            failures.append({
                'status': status,
                'url': url,
                'section': section.title
            })
    return failures

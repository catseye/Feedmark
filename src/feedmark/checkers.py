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


def check_links(documents):
    links = extract_links_from_documents(documents)

    failures = []
    for url, section in tqdm(links, total=len(links)):
        try:
            r = requests.head(url)
            status = r.status_code
        except Exception as e:
            status = str(e)
        if status != 200:
            failures.append((status, url, section))
    return failures

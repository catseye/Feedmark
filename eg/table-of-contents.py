#
# Example of a Python script that creates a table of contents from
# the JSON extracted by feedmark from a set of Feedmark documents.
#

import json
import re
import subprocess
import sys
import urllib


def generate_toc_line(document):
    title = document['title']
    filename = urllib.quote(document['filename'])
    sections = document.get('sections', [])
    properties = document.get('properties', {})

    # You may wish to display some information after each entry in the ToC.  Here are some examples.
    signs = []

    # Display a count of the sections in the document.
    section_count = len(sections)
    signs.append('({})'.format(section_count))

    # Display (U) if the document is under construction.
    if properties.get('status') == 'under construction':
        signs.append('*(U)*')

    # Display the year of publication, if the document provides a publication-date.
    if properties.get('publication-date'):
        pubdate = properties['publication-date']
        match = re.search(r'(\w+\s+\d\d\d\d)', pubdate)
        if match:
            pubdate = match.group(1)
        signs.append('({})'.format(pubdate))

    return "*   [{}]({}) {}\n".format(title, filename, ' '.join(signs))


def output_toc(filenames):
    data = json.loads(subprocess.check_output(["feedmark", "--output-json"] + filenames))
    for document in data['documents']:
        line = generate_toc_line(document)
        sys.stdout.write(line)


if __name__ == '__main__':
    output_toc([
        'Recent Llama Sightings.md',
        'Ancient Llama Sightings.md',
    ])

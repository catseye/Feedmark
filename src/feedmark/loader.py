import codecs
import json
import sys

from feedmark.parser import Parser
from feedmark.utils import items


def read_document_from(filename):
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
    parser = Parser(markdown_text)
    document = parser.parse_document()
    document.filename = filename
    return document


def read_refdex_from(filenames, input_refdex_filename_prefix=None):
    refdex = {}
    for filename in filenames:
        try:
            with codecs.open(filename, 'r', encoding='utf-8') as f:
                local_refdex = json.loads(f.read())
                if input_refdex_filename_prefix:
                    for key, value in items(local_refdex):
                        if 'filename' in value:
                            value['filename'] = input_refdex_filename_prefix + value['filename']
                        if 'filenames' in value:
                            value['filenames'] = [input_refdex_filename_prefix + f for f in value['filenames']]
                refdex.update(local_refdex)
        except:
            sys.stderr.write("Could not read refdex JSON from '{}'\n".format(filename))
            raise

    # Python 2/3
    try:
        unicode_string = unicode
    except NameError:
        unicode_string = str

    for key, value in items(refdex):
        try:
            assert isinstance(key, unicode_string)
            if 'url' in value:
                assert len(value) == 1
                assert isinstance(value['url'], unicode_string)
                value['url'].encode('utf-8')
            elif 'filename' in value and 'anchor' in value:
                assert len(value) == 2
                assert isinstance(value['filename'], unicode_string)
                value['filename'].encode('utf-8')
                assert isinstance(value['anchor'], unicode_string)
                value['anchor'].encode('utf-8')
            elif 'filenames' in value and 'anchor' in value:
                assert len(value) == 2
                for filename in value['filenames']:
                    assert isinstance(value, unicode_string)
                    filename.encode('utf-8')
                assert isinstance(value['anchor'], unicode_string)
                value['anchor'].encode('utf-8')
            else:
                raise NotImplementedError("badly formed refdex")
        except:
            sys.stderr.write("Component of refdex not suitable: '{}: {}'\n".format(repr(key), repr(value)))
            raise

    return refdex


def convert_refdex_to_single_filename_refdex(input_refdex):
    """Note that this makes a partially shallow copy."""
    refdex = {}
    for key, value in input_refdex.items():
        if 'filenames' in value:
            refdex[key] = {
                'filename': value['filenames'][-1],
                'anchor': value['anchor']
            }
        else:
            refdex[key] = value
    return refdex

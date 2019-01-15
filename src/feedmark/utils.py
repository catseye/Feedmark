# Python 2/3
try:
    unicode = unicode
except NameError:
    unicode = str

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
assert StringIO

try:
    from urllib import quote, quote_plus
except ImportError:
    from urllib.parse import quote, quote_plus
assert quote and quote_plus


def items(d):
    try:
        return d.iteritems()
    except AttributeError:
        return d.items()


def items_in_priority_order(di, priority):
    for key in priority:
        if key in di:
            yield key, di[key]
    for key, item in sorted(items(di)):
        if key not in priority:
            yield key, item

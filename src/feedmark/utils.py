try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus
assert quote_plus


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

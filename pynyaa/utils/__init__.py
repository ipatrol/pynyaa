
import math

from flask import request, url_for, current_app, g
from markupsafe import Markup

from . import bencode


def pretty_size(size):
    if not size:
        return '0 B'
    exp = min(4, int(math.log(size, 1024)))
    suffix = ['B', 'KiB', 'MiB', 'GiB', 'TiB'][exp]
    size = size / 1024**exp
    return f'{size:.1f} {suffix}'


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


def cdatasafe(text):
    text = text.replace(']]>', '')
    return Markup(text)


def inject_search_data():
    """before_request hook"""
    map_long_names = dict(
        c='category',
        s='status',
        q='query',
    )
    search = dict(
        category='',
        status='',
        sort='',
        order='',
        max='',
        query='',
    )
    for key in request.args:
        if key in ('c', 'category', 's', 'status', 'sort', 'order', 'max', 'q', 'query'):
            search[map_long_names.get(key, key)] = request.args.get(key)

    if 'max' not in search:
        search['max'] = 50

    try:
        search['max'] = int(search['max'])
    except ValueError:
        search['max'] = 50

    search['max'] = min(300, max(5, search['max']))

    current_app.jinja_env.globals['search'] = search
    g.search = search


def decode_torrent(data):
    torrent = bencode.bdecode(data)
    return _decode_unicode(torrent)


def _decode_unicode(value):
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    elif isinstance(value, dict):
        for key in value:
            if key != 'pieces':
                value[key] = _decode_unicode(value[key])
    elif isinstance(value, list):
        for i, item in enumerate(value):
            value[i] = _decode_unicode(item)
    return value


import math

from flask import request, url_for
from markupsafe import Markup


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


from flask import Blueprint, render_template, abort, request

from .. import models, db

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/page/<int:page>')
@main.route('/search', endpoint='search')
@main.route('/search/<int:page>', endpoint='search')
def home(page=1):
    query = models.Torrent.query\
        .options(
            db.joinedload(models.Torrent.category),
            db.joinedload(models.Torrent.sub_category),
            db.joinedload(models.Torrent.status),
        )

    # c=_&s=&sort=torrent_id&order=desc&max=5&q=
    map_long_names = dict(
        c='category',
        s='status',
        max='maxperpage',
        q='query',
    )
    search = dict(
        category='',
        status='',
        sort='',
        order='',
        maxperpage='',
        query='',
    )
    for key in request.args:
        if key in ('c', 's', 'sort', 'order', 'max', 'q'):
            search[map_long_names.get(key, key)] = request.args.get(key)

    if 'maxperpage' not in search:
        search['maxperpage'] = 50

    try:
        search['maxperpage'] = int(search['maxperpage'])
    except ValueError:
        search['maxperpage'] = 50

    search['maxperpage'] = min(300, max(5, search['maxperpage']))

    if search['category'] and '_' in search['category']:
        cat, subcat = search['category'].split('_', 1)
        if cat and cat.isdigit():
            query = query.filter(models.Torrent.category_id == int(cat))
        if subcat and subcat.isdigit():
            query = query.filter(models.Torrent.sub_category_id == int(subcat))

    if search['status'] and search['status'].isdigit():
        query = query.filter(models.Torrent.status_id == int(search['status']))

    if search['query']:
        words = search['query'].split()
        for word in words:
            query = query.filter(models.Torrent.name.ilike(f'%{word}%'))

    if search['sort'] and search['sort'] in ('id', 'name', 'date', 'downloads'):
        sort_column = getattr(models.Torrent, search['sort'])
    else:
        sort_column = models.Torrent.id

    ordering = 'desc'
    if search['order'] and search['order'] in ('asc', 'desc'):
        ordering = search['order']

    sort_and_ordering = getattr(sort_column, ordering)()
    query = query.order_by(sort_and_ordering)

    pagination = query.paginate(page=page, per_page=search['maxperpage'])
    return render_template('home.html', search=search, torrents_pagination=pagination)


@main.route('/api/<int:page>')
def api(page):
    pass


@main.route('/api/view/<int:torrent_id>')
def api_view(torrent_id):
    pass


@main.route('/faq')
def faq():
    pass


@main.route('/feed.xml')
def feed():
    pass


@main.route('/view/<int:torrent_id>')
def torrent_view(torrent_id):
    torrent = models.Torrent.query.filter_by(id=torrent_id).first()
    if torrent is None:
        return abort(404)
    return render_template('view.html', torrent=torrent)

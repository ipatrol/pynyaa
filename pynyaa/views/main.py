
from flask import Blueprint, render_template, abort, request, Response, g

from .. import models, db

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/page/<int:page>')
@main.route('/search', endpoint='search')
@main.route('/search/<int:page>', endpoint='search')
@main.route('/feed.xml', endpoint='feed')
def home(page=1):
    query = models.Torrent.query\
        .options(
            db.joinedload(models.Torrent.category),
            db.joinedload(models.Torrent.sub_category),
            db.joinedload(models.Torrent.status),
        )

    # no point in listing torrents that don't have hashes or filesizes
    query = query.filter(db.and_(
        models.Torrent.hash.isnot(None),
        models.Torrent.hash != '',
        models.Torrent.filesize != 0
    ))

    search = g.search
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

    pagination = query.paginate(page=page, per_page=search['max'])
    if request.endpoint == 'main.feed':
        return Response(
            render_template('feed.xml', torrents_pagination=pagination),
            mimetype='application/xml')
    else:
        return render_template('home.html', torrents_pagination=pagination)


@main.route('/api/<int:page>')
def api(page):
    pass


@main.route('/api/view/<int:torrent_id>')
def api_view(torrent_id):
    pass


@main.route('/faq')
def faq():
    return render_template('faq.html')


@main.route('/view/<int:torrent_id>')
def torrent_view(torrent_id):
    torrent = models.Torrent.query\
        .options(
            db.joinedload(models.Torrent.category),
            db.joinedload(models.Torrent.sub_category),
            db.joinedload(models.Torrent.status),
            db.joinedload(models.Torrent.comments).joinedload(models.Comment.user),
        ).filter_by(id=torrent_id).first()
    if torrent is None:
        return abort(404)
    return render_template('view.html', torrent=torrent)

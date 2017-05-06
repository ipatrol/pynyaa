
import hashlib
from datetime import datetime

from flask import Blueprint, render_template, abort, request, Response, g, redirect, url_for
import pytz

from .. import models, db, forms
from .. import utils

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
        if len(search['query']) == 40 and all(char in '0123456789abcdef'
                                              for char in search['query'].lower()):
            query = query.filter(models.Torrent.hash == search['query'].lower())
        else:
            words = search['query'].split()
            for word in words:
                query = query.filter(models.Torrent.name.ilike(f'%{word}%'))

    if search['sort'] and search['sort'] in ('id', 'name', 'date', 'downloads'):
        sort_column = getattr(models.Torrent, search['sort'])
    else:
        sort_column = models.Torrent.id
        search['sort'] = 'id'

    ordering = 'desc'
    if search['order'] and search['order'] in ('asc', 'desc'):
        ordering = search['order']
    search['order'] = ordering

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


@main.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload torrent file.

    Possibly requires some more sanity checks.
    """
    upload_form = forms.UploadTorrentForm()

    cats = {}
    for cat in models.Category.query.order_by(models.Category.name):
        cats[f'{cat.id}_'] = cat.name
        for subcat in cat.sub_categories:
            cats[f'{cat.id}_{subcat.id}'] = f'{cat.name} - {subcat.name}'
    upload_form.category.choices = cats.items()

    if upload_form.validate_on_submit():
        torrent_file = upload_form.data['torrent']
        category = upload_form.data.get('category')
        if category not in cats:
            return abort(400, 'Invalid category')

        try:
            torrent_data = utils.decode_torrent(torrent_file.stream.read())
        except utils.bencode.BTFailure:
            return abort(400, 'Invalid torrent file')

        # announce, comment, created by, creation date, info
        try:
            bencoded_info = utils.bencode.bencode(torrent_data['info'])
        except utils.bencode.BTFailure as exc:
            return abort(400, str(exc))
        info_hash = hashlib.sha1(bencoded_info).hexdigest()

        # two types of torrents:
        # single file:
        #   length, name, piece length, pieces

        # multiple files:
        #   files, name, piece length, pieces

        # info keys: length, name, piece length, pieces
        info = torrent_data['info']

        torrent = models.Torrent()
        torrent.name = info['name']
        torrent.hash = info_hash

        cat, subcat = category.split('_', 1)
        torrent.category_id = cat
        if subcat:
            torrent.sub_category_id = subcat

        torrent.description = upload_form.data.get('description')
        torrent.website_link = upload_form.data.get('website')
        torrent.downloads = 0
        torrent.stardom = 0
        torrent.date = datetime.now(pytz.utc)

        torrent.t_announce = torrent_data['announce']
        torrent.t_comment = torrent_data['comment']
        torrent.t_created_by = torrent_data['created by']
        torrent.t_creation_date = datetime.fromtimestamp(
            torrent_data['creation date'], pytz.utc)

        torrent.is_exact = True
        if 'files' in info:
            torrent.filesize = 0
            for file_data in info['files']:
                torrent.filesize += file_data['length']
                torrent.files.append(models.File(
                    path='/'.join(file_data['path']),
                    size=file_data['length']
                ))
        else:
            torrent.filesize = info['length']
            torrent.files.append(models.File(
                path=torrent.name,
                size=torrent.filesize
            ))
        db.session.add(torrent)
        db.session.commit()
        return redirect(url_for('.torrent_view', torrent_id=torrent.id))

    return render_template('upload.html', form=upload_form)

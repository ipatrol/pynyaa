

from flask import Blueprint, abort, jsonify

from .. import models, utils


api = Blueprint('api', __name__)


@api.route('/filelist/<int:torrent_id>')
def filelist(torrent_id):
    torrent = models.Torrent.query.filter_by(id=torrent_id).first()
    if torrent is None:
        return abort(404)
    files = []
    for file in torrent.files:
        files.append(dict(
            path=file.path,
            size=file.size,
            pretty_size=utils.pretty_size(file.size),
        ))
    return jsonify(
        id=torrent.id,
        files=files
    )

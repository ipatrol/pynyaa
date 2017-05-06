
import pathlib
import zipfile
import sqlite3
from datetime import datetime
import time
import zlib
import json

from flask_script import Manager
import pytz

from pynyaa import create_app, db, models

config_file = pathlib.Path('config/development.py')
app = create_app(config_file.absolute())

manager = Manager(app)


def extract_comment(text):
    if text.startswith('<div class="cmain">'):
        text = text[19:]
    if text.endswith('</div>'):
        text = text[:-6]
    return text


def normalize_filesize(size):
    """Takes string like "123 MiB" and converts it into integer of bytes."""
    if size is None or not size:
        return 0
    size, suffix = size.rsplit(maxsplit=1)
    try:
        size = float(size.strip())
    except ValueError:
        return 0
    suffix_map = dict(b=0, kib=1, mib=2, gib=3, tib=4)
    suffix = suffix.lower()
    if suffix not in suffix_map:
        return int(size)
    return int(size * 1024**suffix_map[suffix])


@manager.command
@manager.option(help='Path to sqlite3 nyaa data dump zip file.')
@manager.option(help='Desctination of unzipped data dump (default: ./import).')
def import_sqlite(path, destination='import'):
    db.drop_all()
    db.create_all()

    filename = 'merged.sqlite3'
    destination = pathlib.Path(destination).absolute()
    sqlite_file = pathlib.Path(destination, filename)

    if not sqlite_file.exists():
        destination.mkdir(0o755, True, True)
        zf = zipfile.ZipFile(path)
        zf.extract(filename, destination)

    with sqlite3.connect(str(sqlite_file)) as conn:
        cursor = conn.cursor()

        for row in cursor.execute('SELECT category_id, category_name FROM categories'):
            db.session.add(models.Category(**dict(zip(('id', 'name'), row))))

        for row in cursor.execute('SELECT status_id, status_name FROM statuses'):
            status_dict = dict(zip(('id', 'name'), row))
            if status_dict['name'] == 'a+':
                status_dict['name'] = 'aplus'

            status_dict['label'] = dict(
                normal='Normal',
                remake='Filter Remakes',
                trusted='Trusted',
                aplus='A+',
            ).get(status_dict['name'], status_dict['name'])
            status = models.Status(**status_dict)
            db.session.add(status)

        for row in cursor.execute('SELECT sub_category_id, parent_id, sub_category_name '
                                  'FROM sub_categories'):
            db.session.add(models.SubCategory(**dict(zip(('id', 'parent_id', 'name'), row))))
        db.session.commit()

        # now the torrents
        tbl_fields = ['torrent_id', 'torrent_name', 'torrent_hash', 'category_id',
                      'sub_category_id', 'status_id', 'date', 'downloads', 'stardom', 'filesize',
                      'description', 'website_link', 'comments']
        fields = tbl_fields[:]
        fields[0:3] = ['id', 'name', 'hash']

        torrent_count, = cursor.execute('SELECT COUNT(*) FROM torrents').fetchone()

        users = set()
        user_status = {}
        start_time = datetime.now(pytz.utc)

        for torrent_number, row in enumerate(
                cursor.execute(f'SELECT {",".join(tbl_fields)} FROM torrents'),
                start=1):

            rowdict = dict(zip(fields, row))
            if rowdict['date'] is None:
                rowdict['date'] = int(time.time())
            rowdict['date'] = datetime.fromtimestamp(rowdict['date'], pytz.utc)

            if isinstance(rowdict['hash'], bytes):
                rowdict['hash'] = rowdict['hash'].decode('ascii')

            if rowdict['hash'] is not None and len(rowdict['hash']) == 40:
                rowdict['hash'] = str(rowdict['hash']).lower()
            else:
                rowdict['hash'] = ''

            if rowdict['description']:
                try:
                    rowdict['description'] = zlib.decompress(rowdict['description']).decode('utf-8')
                except Exception as exc:
                    rowdict['description'] = ''

            rowdict['filesize'] = normalize_filesize(rowdict['filesize'])
            rowdict['is_exact'] = False

            if rowdict['comments']:
                try:
                    comments = json.loads(zlib.decompress(rowdict['comments']).decode('utf-8'))
                except Exception as exc:
                    comments = []

                for json_comment in comments:
                    if json_comment['ui'] not in users:
                        if json_comment['us'] not in user_status:
                            user_status[json_comment['us']] = models.UserStatus(
                                name=json_comment['us']
                            )
                            db.session.add(user_status[json_comment['us']])
                        user = models.User(
                            id=json_comment['ui'],
                            name=json_comment['un'],
                            status=user_status[json_comment['us']]
                        )
                        db.session.add(user)
                        users.add(json_comment['ui'])
                    comment = models.Comment(
                        id=int(json_comment['id'].lstrip('c')),
                        text=extract_comment(json_comment['c']),
                        av=json_comment['av'],
                        date=datetime.fromtimestamp(json_comment['t'], pytz.utc)
                    )
                    db.session.add(comment)
            del rowdict['comments']
            db.session.add(models.Torrent(**rowdict))

            # time already spent
            delta_time = datetime.now(pytz.utc) - start_time
            # time per torrent
            tpt = delta_time.total_seconds() / torrent_number
            rest = int((torrent_count - torrent_number) * tpt)
            eta = f'{rest//60:02d}:{rest%60:02d}'

            print(f'{torrent_number/torrent_count*100:.2f} % -'
                  f' {torrent_number} / {torrent_count} - ETA: {eta}',
                  end='      \r')
            if torrent_number % 100 == 0:
                db.session.commit()

        db.session.commit()


@manager.command
def run():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    manager.run()

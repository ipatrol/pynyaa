
from .. import db


class Torrent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))
    hash = db.Column(db.String(40))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='torrents')

    sub_category_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'))
    sub_category = db.relationship('SubCategory', backref='torrents')

    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status = db.relationship('Status', backref='torrents')

    date = db.Column(db.DateTime(True))
    downloads = db.Column(db.Integer)
    stardom = db.Column(db.Integer)
    filesize = db.Column(db.BigInteger)
    is_exact = db.Column(db.Boolean)

    description = db.Column(db.Text)
    website_link = db.Column(db.String(1024))

    @property
    def cat_url_param(self):
        return f'{self.category_id}_{self.sub_category_id}'

    @property
    def magnet(self):
        return f'magnet:?xt=urn:sha1:{self.hash.upper()}'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))


class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))

    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    parent = db.relationship('Category', backref='sub_categories')

    @property
    def image_url(self):
        return f'img/torrents/{self.id}.png'


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    label = db.Column(db.String(50))

    @property
    def css_class(self):
        if self.name == 'a+':
            return 'aplus'
        return self.name


class UserStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)

    status_id = db.Column(db.Integer, db.ForeignKey('user_status.id'))
    status = db.relationship('UserStatus', backref='users')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime(True))
    av = db.Column(db.String(255))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='comments')

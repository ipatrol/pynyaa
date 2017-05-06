
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class UploadTorrentForm(FlaskForm):
    torrent = FileField(validators=[DataRequired()])
    category = SelectField(validators=[DataRequired()])
    website = StringField()
    description = TextAreaField()

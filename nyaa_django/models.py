# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals
import itertools

from django.contrib.auth import get_user_model
from django.contrib.auth import models as auth
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.postgres.fields import ArrayField

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category'

class Status(models.Model):
    name = models.CharField(max_length=20, blank=True, null=True)
    label = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'status'


class SubCategory(models.Model):
    name = models.CharField(max_length=1024, blank=True, null=True)
    parent = models.ForeignKey(Category, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sub_category'


class Torrent(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=1024)
    hash = models.CharField(max_length=40)
    is_sqlite_import = models.NullBooleanField()
    category = models.ForeignKey(Category, blank=True, null=True)
    sub_category = models.ForeignKey(SubCategory, blank=True, null=True)
    status = models.ForeignKey(Status, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    downloads = models.IntegerField(blank=True, null=True)
    stardom = models.IntegerField(blank=True, null=True)
    filesize = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website_link = models.CharField(max_length=1024, blank=True, null=True)
    t_creation_date = models.DateTimeField(blank=True, null=True)
    t_created_by = models.CharField(max_length=255, blank=True, null=True)
    t_comment = models.TextField(blank=True, null=True)
    t_announce = models.TextField(blank=True, null=True)
    file_paths = ArrayField(
        models.CharField(max_length=1024
        ), blank=True, null=True)
    file_sizes = ArrayField(
        models.BigIntegerField(blank=True, null=True),
        blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    @property
    def magnet(self):
        return "magnet:?xt=urn:btih:{}&dn={}&tr=udp://zer0day.to:1337/announce\
    &tr=udp://tracker.leechers-paradise.org:6969&tr=udp://explodie.org:6969&\
    tr=udp://tracker.opentrackr.org:1337&tr=udp://tracker.coppersurfer.tk:6969\
    &tr=http://tracker.baka-sub.cf/announce&\
    tr=http://tracker.sukebei.nyaa.rip:69/announce&\
    https://tracker.sukebei.nyaa.rip/announce".format(
                    self.hash, self.name)
    @property
    def file_info(self):
        return itertools.izip(self.file_paths,self.file_sizes)
    class Meta:
        managed = False
        db_table = 'torrent'

class Comment(models.Model):
    text = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    av = models.CharField(max_length=255, blank=True, null=True)
    old_user_name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    torrent = models.ForeignKey(Torrent, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment'
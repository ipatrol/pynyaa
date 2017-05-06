from django.db import models


# Create your models here.


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categories'


class Statuses(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'statuses'


class SubCategories(models.Model):
    sub_category_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(Categories, models.DO_NOTHING, blank=True, null=True)
    sub_category_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sub_categories'


class Torrents(models.Model):
    torrent_id = models.BigAutoField(primary_key=True)
    torrent_name = models.TextField(blank=True, null=True)
    torrent_hash = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Categories, models.DO_NOTHING, blank=True, null=True)
    sub_category = models.ForeignKey(SubCategories, models.DO_NOTHING, blank=True, null=True)
    status = models.ForeignKey(Statuses, models.DO_NOTHING, blank=True, null=True)
    downloads = models.IntegerField(blank=True, null=True)
    stardom = models.SmallIntegerField(blank=True, null=True)
    filesize = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website_link = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'torrents'

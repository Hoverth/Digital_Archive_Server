from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Archiver Models

class Archiver(models.Model):
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=32)
    base_url = models.CharField(max_length=255)
    about = models.TextField(null=True, blank=True)
    related_types = models.TextField(default='')
    adult = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ('can_archive', 'Can order archival')
        ]

    def __str__(self):
        return str(self.codename) + '  //  ' + str(self.name)


# Content Models

class Tag(models.Model):
    # Standard Fields
    name = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255, default='', blank=True)
    source_url = models.CharField(max_length=255, default='', blank=True)
    source_id = models.CharField(max_length=255, default='', blank=True)
    adult = models.BooleanField(default=False, blank=True)

    # Additional Fields
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This tag has no generated preview</p>')
    from_archiver = models.ForeignKey(Archiver, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.tag_id) + '  //  ' + str(self.name)


class Creator(models.Model):
    # Standard Fields
    name = models.CharField(max_length=255)
    creator_id = models.CharField(max_length=255, default='', blank=True)
    about = models.TextField(default='', blank=True)
    source_url = models.CharField(max_length=255, default='', blank=True)
    source_id = models.CharField(max_length=255, default='', blank=True)
    adult = models.BooleanField(default=False, blank=True)

    # Additional Fields
    related_creators = models.ManyToManyField('self', blank=True)
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This creator has no generated preview</p>')
    from_archiver = models.ForeignKey(Archiver, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.creator_id) + '  //  ' + str(self.name)


class Content(models.Model):
    # Standard Fields
    title = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255)
    source_id = models.CharField(max_length=255)
    content_path = models.CharField(max_length=255)
    time_retrieved = models.DateTimeField(default=timezone.now)
    creators = models.ManyToManyField('Creator', related_name='content_creators', blank=True)
    tags = models.ManyToManyField('Tag', related_name='content_tags', blank=True)
    notes = models.TextField(default='', blank=True)
    time_created = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=255, default='', blank=True)
    copyright = models.CharField(max_length=255, default='', blank=True)
    related_content = models.ManyToManyField('self', blank=True)

    # Additional Fields
    published_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    content_size = models.PositiveIntegerField()
    seen_by = models.ManyToManyField(User, related_name='content_seen_by', blank=True)
    liked_by = models.ManyToManyField(User, related_name='content_liked_by', blank=True)
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This content has no generated preview</p>')
    from_archiver = models.ForeignKey(Archiver, on_delete=models.RESTRICT, null=True)

    class Meta:
        permissions = [
            ('adult_content', 'Can View 18+ content')
        ]

    def __str__(self):
        return str(self.content_type) + '  //  ' + str(self.title)


class Collection(models.Model):
    name = models.CharField(max_length=255, default='Collection')
    owners = models.ManyToManyField(User, related_name='collection_owners')
    restricted_access = models.BooleanField(default=False, blank=True)
    can_access = models.ManyToManyField(User, related_name='collection_can_access', blank=True)
    content = models.ManyToManyField(Content, related_name='collection_content', blank=True)
    related_collections = models.ManyToManyField('self', blank=True)
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This collection has no generated preview</p>')
    adult = models.BooleanField(default=False, blank=True)
    search = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

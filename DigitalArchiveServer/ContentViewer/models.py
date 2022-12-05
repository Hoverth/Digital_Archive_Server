from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Tag(models.Model):
    # Standard Fields
    name = models.CharField(max_length=255)
    tag_id = models.CharField(max_length=255, null=True)
    source_url = models.CharField(max_length=255, null=True)
    source_id = models.CharField(max_length=255, null=True)

    # Additional Fields
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This tag has no generated preview</p>')

    def __str__(self):
        return str(self.tag_id) + '  //  ' + str(self.name)


class Creator(models.Model):
    # Standard Fields
    name = models.CharField(max_length=255)
    creator_id = models.CharField(max_length=255, null=True)
    about = models.TextField(null=True)
    source_url = models.CharField(max_length=255, null=True)
    source_id = models.CharField(max_length=255, null=True)

    # Additional Fields
    related_creators = models.ManyToManyField('self')
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This creator has no generated preview</p>')

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
    creators = models.ManyToManyField('Creator', related_name='content_creators')
    tags = models.ManyToManyField('Tag', related_name='content_tags')
    notes = models.TextField(null=True)
    time_created = models.DateTimeField(null=True)
    language = models.CharField(max_length=255, null=True)
    copyright = models.CharField(max_length=255, null=True)
    related_content = models.ManyToManyField('self')

    # Additional Fields
    published_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)
    content_size = models.PositiveIntegerField()
    seen_by = models.ManyToManyField(User, related_name='content_seen_by')
    liked_by = models.ManyToManyField(User, related_name='content_liked_by')
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This content has no generated preview</p>')

    def __str__(self):
        return str(self.content_type) + '  //  ' + str(self.title)


class Collection(models.Model):
    name = models.CharField(max_length=255, default='Collection')
    owners = models.ManyToManyField(User, related_name='collection_owners')
    restricted_access = models.BooleanField(default=False)
    can_access = models.ManyToManyField(User, related_name='collection_can_access')
    content = models.ManyToManyField(Content, related_name='collection_content')
    related_collections = models.ManyToManyField('self')
    preview = models.CharField(max_length=512, default='<p class=\'preview\'>This collection has no generated preview</p>')

    def __str__(self):
        return str(self.name)

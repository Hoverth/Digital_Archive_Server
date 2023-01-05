from django.contrib.auth.models import User, Group, Permission, ContentType
from .models import Archiver, Content, Tag


def populate_models(sender, **kwargs):
    if not Tag.objects.filter(tag_id='adult-content').exists():
        adult_content_tag = Tag()
        adult_content_tag.name = "Adult Content"
        adult_content_tag.tag_id = "adult-content"
        adult_content_tag.adult = True
        adult_content_tag.save()

    if not Group.objects.filter(name='Adults'):
        if not Permission.objects.filter(codename='adult_content').exists():
            adult_content_permission = Permission()
            adult_content_permission.name = 'Can View 18+ content'
            adult_content_permission.codename = 'adult_content'
            adult_content_permission.content_type = ContentType.objects.get_for_model(Content)
            adult_content_permission.save()
        else:
            adult_content_permission = Permission.objects.get(codename='adult_content')

        adult_content_group = Group()
        adult_content_group.name = "Adults"
        adult_content_group.save()
        adult_content_group.permissions.add(adult_content_permission)
        adult_content_group.save()

    if not Group.objects.filter(name='Archivists'):
        if not Permission.objects.filter(codename='can_archive').exists():
            archiver_permission = Permission()
            archiver_permission.name = 'Can order archival'
            archiver_permission.codename = 'can_archive'
            archiver_permission.content_type = ContentType.objects.get_for_model(Archiver)
            archiver_permission.save()
        else:
            archiver_permission = Permission.objects.get(codename='can_archive')

        archiver_group = Group()
        archiver_group.name = "Archivists"
        archiver_group.save()
        archiver_group.permissions.add(archiver_permission)
        archiver_group.save()

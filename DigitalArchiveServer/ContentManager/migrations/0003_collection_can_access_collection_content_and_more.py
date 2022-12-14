# Generated by Django 4.1.3 on 2022-12-04 23:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ContentManager', '0002_alter_collection_related_collections_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='can_access',
            field=models.ManyToManyField(related_name='collection_can_access', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='collection',
            name='content',
            field=models.ManyToManyField(related_name='collection_content', to='ContentManager.content'),
        ),
        migrations.AddField(
            model_name='collection',
            name='name',
            field=models.CharField(default='Collection', max_length=255),
        ),
        migrations.AddField(
            model_name='collection',
            name='owners',
            field=models.ManyToManyField(related_name='collection_owners', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='collection',
            name='restricted_access',
            field=models.BooleanField(default=False),
        ),
    ]
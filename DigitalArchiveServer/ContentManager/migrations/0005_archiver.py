# Generated by Django 4.1.3 on 2022-12-08 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ContentManager', '0004_alter_collection_can_access_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Archiver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=16)),
                ('base_url', models.CharField(max_length=255)),
                ('about', models.TextField(blank=True, null=True)),
            ],
        ),
    ]

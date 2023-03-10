# Generated by Django 4.1.3 on 2022-12-21 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ContentManager', '0010_archiver_adult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='copyright',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='content',
            name='language',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='content',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]

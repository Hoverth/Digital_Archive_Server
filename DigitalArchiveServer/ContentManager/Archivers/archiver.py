import pathlib
import json

from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponseNotFound

from celery import shared_task

from . import ArchiveWorker, GenericArchiveWorker
from ..settings import STATIC_ROOT
from ..models import Content, Tag, Creator

archive_workers = [
    GenericArchiveWorker.GenericArchiveWorker
]


def view_archive_tools(request):
    if not request.user.is_authenticated or not request.user.has_perm('ContentManager.can_archive'):
        return redirect('/')
    if request.method == 'POST':
        if 'scan-library' in request.POST:
            scan_library_for_existing_content.delay()
        if 'generate-previews' in request.POST:
            generate_previews.delay()

    workers = archive_workers
    if not request.user.has_perm('adult_content'):
        workers = []
        for archive_worker in archive_workers:
            if not archive_worker.adult:
                workers.append(archive_worker)

    context = {
        'archivers': workers
    }
    return render(request, 'Archivers/Archivers.html', context=context)


def view_archiver(request, codename):
    if not request.user.is_authenticated or not request.user.has_perm('ContentManager.can_archive'):
        return redirect('/')

    response = HttpResponseNotFound('Page not found')  # set default to be a 404
    for archive_worker in archive_workers:
        instance = archive_worker()
        if instance.codename == codename:
            if (request.user.has_perm('adult_content') and instance.adult) or not instance.adult:
                response = instance.as_view(request)
            else:
                return redirect('/')
    return response


def log_print(message):
    log_path = pathlib.Path(STATIC_ROOT)

    log_path.mkdir(parents=True, exist_ok=True)
    for parent_directory in reversed(pathlib.Path(log_path).parents):
        parent_directory.mkdir(exist_ok=True, mode=0o777)

    log_path = log_path / 'general_log.txt'

    if not log_path.exists():
        log_path.touch()

    with log_path.open(mode='a') as log_file:
        log_file.write(message + '\n')


@shared_task
def scan_library_for_existing_content():

    number_of_scanned_content = 0

    content_path = pathlib.Path(STATIC_ROOT)
    for file in content_path.rglob('*.meta'):
        # validate metafile
        # import metafile
        with open(file, 'r') as metafile:
            try:
                metadata = json.loads(metafile.read())
            except json.JSONDecodeError:
                continue

        if ArchiveWorker.check_metadata(metadata):
            content_path = str(file.parent).replace(STATIC_ROOT, '').strip('/')
            if metadata['content-path'] is not content_path:
                metadata['content-path'] = content_path

            saved_content = False
            if len(archive_workers) != 0:
                for archive_worker in archive_workers:
                    if archive_worker().codename in metadata['content-type']:
                        archive_worker().save_content(metadata)

                        # perhaps this would work for a global setting
                        # archive_worker().get_content(metadata['source-url'])

                        saved_content = True
                        break

            if not saved_content:
                GenericArchiveWorker.GenericArchiveWorker().save_content(metadata)

            number_of_scanned_content += 1
            log_print(str(number_of_scanned_content).zfill(6) + ' : Saving: ' + str(content_path))

        else:
            log_print('Content metadata failed schema: ' + str(content_path))

    generate_previews.delay()
    log_print('\n Scanning Files Complete!\n')


@shared_task
def generate_previews():
    for content in Content.objects.order_by('title'):
        if content.preview == '<p class=\'preview\'>This content has no generated preview</p>':
            content.preview = ArchiveWorker.ArchiveWorker.make_preview(content.content_path)
            content.save()

    # generate tag & creator previews
    for tag in Tag.objects.order_by('name'):
        try:
            tag.preview = Content.objects.filter(tags__id=tag.id).order_by('-time_retrieved').first().preview
            tag.save()
        except (ValueError, AttributeError):
            tag.preview = '<p class=\'preview\'>This tag has no generated preview</p>'
            tag.save()
    log_print('\nGenerated Tag previews')

    for creator in Creator.objects.order_by('name'):
        try:
            creator.preview = Content.objects.filter(creators__id=creator.id).order_by(
                '-time_retrieved').first().preview
            creator.save()
        except (ValueError, AttributeError):
            creator.preview = '<p class=\'preview\'>This creator has no generated preview</p>'
            creator.save()
    log_print('\nGenerated Creator previews')


app_name = 'Archivers'
urlpatterns = [
    path('', view_archive_tools, name='index'),
    path('<str:codename>', view_archiver, name='archiver')
]

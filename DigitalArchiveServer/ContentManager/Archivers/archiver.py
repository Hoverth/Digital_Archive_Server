import pathlib
import json

from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseNotFound

from . import ArchiveWorker
from ..settings import STATIC_ROOT
from ..models import Content, Tag, Creator

archive_workers = []


def view_archive_tools(request):
    context = {
        'archivers': archive_workers
    }
    return render(request, 'Archivers/Archivers.html', context=context)


def view_archiver(request, codename):
    response = HttpResponseNotFound('Page not found')  # set default to be a 404
    for archive_worker in archive_workers:
        instance = archive_worker()
        if instance.codename == codename:
            response = instance.as_view(request)
    return response


def scan_library_for_existing_content(request):
    content_path = pathlib.Path(STATIC_ROOT)
    lines = []
    for file in content_path.rglob('*'):
        # validate metafile
        # import metafile
        if '.meta' in file.name:
            with open(file, 'r') as metafile:
                metadata = json.loads(metafile.read())
                lines.append(json.dumps(metadata, indent=4).replace('\n', '<br>') + '<br><br>')

            if ArchiveWorker.check_metadata(metadata):
                content_path = str(file.parent).replace(STATIC_ROOT, '').strip('/')
                if metadata['content-path'] is not content_path:
                    metadata['content-path'] = content_path

                for archive_worker in archive_workers:
                    if archive_worker().base_url in metadata['source_url']:
                        archive_worker().get_content(metadata['source_url'])
                    else:
                        ArchiveWorker.ArchiveWorker().save_content(metadata)
                if len(archive_workers) == 0:
                    ArchiveWorker.ArchiveWorker().save_content(metadata)
            else:
                lines.append('failed schema: ' + metadata['title'])

    # generate tag & creator previews
    for tag in Tag.objects.order_by('name'):
        try:
            tag.preview = Content.objects.filter(tags__id=tag.id).order_by('-time_retrieved').first().preview
            tag.save()
        except ValueError:
            tag.preview = '<p class=\'preview\'>This tag has no generated preview</p>'
            tag.save()

    for creator in Creator.objects.order_by('name'):
        try:
            creator.preview = Content.objects.filter(creators__id=creator.id).order_by(
                '-time_retrieved').first().preview
            creator.save()
        except ValueError:
            creator.preview = '<p class=\'preview\'>This creator has no generated preview</p>'
            creator.save()

    return render(request, 'ContentManager/scan.html', {'lines': lines})


app_name = 'Archivers'
urlpatterns = [
    path('', view_archive_tools, name='index'),
    path('<str:codename>', view_archiver, name='archiver'),
    path('scan', scan_library_for_existing_content)
]

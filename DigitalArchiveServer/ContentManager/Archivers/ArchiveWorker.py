import requests
import pathlib
import time
import json
import jsonschema

import lxml
from bs4 import BeautifulSoup

from celery import shared_task

from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from ..settings import STATIC_ROOT, STATIC_URL
from ..models import Content, Archiver, Tag, Creator

metadata_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Metafile",
    "description": "A Metadata JSON File Specification",
    "type": "object",
    "properties": {
        "title": {
            "description": "The title of the content",
            "type": "string"
        },
        "content-type": {
            "description": "The type of content this content is",
            "type": "string"
        },
        "source-url": {
            "description": "The URL where this content was sourced from",
            "type": "string"
        },
        "source-id": {
            "description": "The ID that the website that this content was sourced from uses to distinguish the content",
            "type": "string"
        },
        "content-path": {
            "description": "The file path that this content has from the top directory",
            "type": "string"
        },
        "time-retrieved": {
            "description": "The EDTF time that this content was retrieved from it's source",
            "type": "string"
        },
        "creators": {
            "description": "The creators of an objects",
            "type": "array",
            "items": {
                "description": "A creator",
                "type": "object",
                "properties": {
                    "creator-name": {
                        "description": "The creator's name",
                        "type": "string"
                    },
                    "creator-id": {
                        "description": "The creator's ID",
                        "type": "string"
                    },
                    "creator-about": {
                        "description": "The creator's description about themselves",
                        "type": "string"
                    },
                    "creator-source-url": {
                        "description": "The source URL for the creator",
                        "type": "string"
                    },
                    "creator-source-id": {
                        "description": "The source ID for the creator",
                        "type": "string"
                    }
                },
                "required": ["creator-name"]
            },
            "uniqueItems": True
        },
        "tags": {
            "description": "The tags an object has",
            "type": "array",
            "items": {
                "description": "A tag",
                "type": "object",
                "properties": {
                    "tag-name": {
                        "description": "The name of the tag",
                        "type": "string"
                    },
                    "tag-id": {
                        "description": "The tag's ID",
                        "type": "string"
                    },
                    "tag-source-url": {
                        "description": "The source URL of the tag",
                        "type": "string"
                    },
                    "tag-source-id": {
                        "description": "The source ID of the tag",
                        "type": "string"
                    }
                },
                "required": ["tag-name"]
            },
            "uniqueItems": True
        },
        "notes": {
            "description": "Misc. notes on the content",
            "type": "string"
        },
        "time-created": {
            "description": "The EDTF time the content was created",
            "type": "string"
        },
        "language": {
            "description": "The language that the content is in (if applicable)",
            "type": "string"
        },
        "copyright": {
            "description": "The copyright of the content (if applicable)",
            "type": "string"
        },
        "related-content": {
            "description": "Other content that this content is related to",
            "type": "array",
            "items": {
                "description": "A piece of related content",
                "type": "object",
                "properties": {
                    "title": {
                        "description": "The title of the related content",
                        "type": "string"
                    },
                    "content-type": {
                        "description": "The type of content this related content is",
                        "type": "string"
                    },
                    "source-url": {
                        "description": "The URL where this related content was sourced from",
                        "type": "string"
                    },
                    "content-path": {
                        "description": "The file path that this related content has from the top directory",
                        "type": "string"
                    },
                    "time-created": {
                        "description": "The EDTF time the related content was created",
                        "type": "string"
                    }
                },
                "required": ["title", "content-type", "source-url", "content-path"]
            },
            "uniqueItems": True
        }
    },
    "required": ["title", "content-type", "source-url", "source-id", "content-path", "time-retrieved"]
}

image_types = ['.gif', '.jpg', '.png']
video_types = ['.mp4', '.mkv']
text_types = ['.txt']

enabled_actions = [
    'get_existing_remote_library',
    'get_content_new',
    'get_content_number',
    'get_content'
]


# this is the class that actually scrapes and builds the archive
class ArchiveWorker:
    name = ''
    codename = ''
    base_url = ''
    about = ''
    adult = False
    enabled_actions = [
        'get_existing_remote_library',
        'get_content_new',
        'get_content_number',
        'get_content'
    ]

    def __init__(self):
        self.register()

    # registers the ArchiveWorker with the website, allowing it to be referred to
    def register(self):
        if not Archiver.objects.filter(codename=self.codename).exists():
            a = Archiver()
            a.name = self.name
            a.codename = self.codename
            a.base_url = self.base_url
            a.adult = self.adult
            a.about = self.about
            a.save()

    def get_model(self):
        return Archiver.objects.get(codename=self.codename)

    class ActionForm(forms.Form):
        ENABLED_ACTIONS = [
            ('get_existing_remote_library', 'get_existing_remote_library'),
            ('get_content_new', 'get_content_new'),
            ('get_content_number', 'get_content_number'),
            ('get_content', 'get_content')
        ]

        action_to_do = forms.ChoiceField(choices=ENABLED_ACTIONS)
        url = forms.URLField(required=False)
        number_of_content_to_get = forms.IntegerField(min_value=0, required=False)

    def as_view(self, request):
        context = {
            'name': self.name,
            'codename': self.codename,
            'base_url': self.base_url,
            'about': self.about,
            'enabled_actions': self.enabled_actions,
            'form': None,
            'error_message': ''
        }
        if request.method == 'POST':
            form = self.ActionForm(request.POST)
            if form.is_valid():
                context['form'] = form
                action = form.cleaned_data['action_to_do']

                self.handle_actions(action, form.cleaned_data)

        else:
            form = self.ActionForm()
            context['form'] = form
        return render(request, 'Archivers/ArchiveWorker.html', context=context)

    # this function handles all the actions requested from the view
    def handle_actions(self, action, data):
        pass

    def save_content(self, metadata):
        metafile_path = pathlib.Path(STATIC_ROOT, metadata['content-path'], '.meta')
        if not metafile_path.exists():
            metafile_path.parent.mkdir(parents=True, exist_ok=True)
            metafile_path.touch()
        with metafile_path.open(mode='w') as metafile:
            metafile.write(json.dumps(metadata))

        if Content.objects.filter(Q(source_url=metadata['source-url'])).exists():
            new_content = Content.objects.filter(Q(source_url=metadata['source-url'])).first()
        else:
            new_content = Content()

        new_content.title = metadata['title'][:255]
        new_content.content_type = metadata['content-type'][:255]
        new_content.source_url = metadata['source-url'][:255]
        new_content.source_id = metadata['source-id'][:255]
        new_content.content_path = metadata['content-path'][:255]
        new_content.published_date = timezone.now()  # metadata['time-retrieved']  # this needs to be converted

        if 'notes' in metadata:
            new_content.notes = metadata['notes']
        if 'time-created' in metadata:
            new_content.time_created = timezone.now()  # metadata['time-created']  # this also needs to be converted
        if 'language' in metadata:
            new_content.language = metadata['language'][:255]
        if 'copyright' in metadata:
            new_content.copyright = metadata['copyright'][:255]

        new_content.content_size = int(pathlib.Path(STATIC_ROOT, metadata['content-path']).stat().st_size)
        new_content.preview = ArchiveWorker.make_preview(metadata['content-path'])[:512]

        new_content.from_archiver = self.get_model()

        new_content.save()

        if 'creators' in metadata and metadata['creators'] is not None:
            for creator in metadata['creators']:
                if Creator.objects.filter(name=creator['creator-name']).exists():
                    new_creator = Creator.objects.filter(name=creator['creator-name']).first()
                else:
                    new_creator = Creator()
                new_creator.name = creator['creator-name'][:255]
                if 'creator-id' in creator:
                    new_creator.creator_id = creator['creator-id'][:255]
                if 'creator-about' in creator:
                    new_creator.about = creator['creator-about']
                if 'creator-source-url' in creator:
                    new_creator.source_url = creator['creator-source-url'][:255]
                if 'creator-source-id' in creator:
                    new_creator.source_id = creator['creator-source-id'][:255]
                if 'adult' in creator:
                    new_creator.adult = bool(creator['adult'])
                new_creator.save()

                new_creator.from_archiver = self.get_model()
                new_creator.save()

                new_content.creators.add(new_creator)

        if 'tags' in metadata and metadata['tags'] is not None:
            for tag in metadata['tags']:
                if Tag.objects.filter(name=tag['tag-name']).exists():
                    new_tag = Tag.objects.filter(name=tag['tag-name']).first()
                else:
                    new_tag = Tag()
                new_tag.name = tag['tag-name'][:255]
                if 'tag-id' in tag:
                    new_tag.tag_id = tag['tag-id'][:255]
                if 'tag-source-url' in tag:
                    new_tag.source_url = tag['tag-source-url'][:255]
                if 'tag-source-id' in tag:
                    new_tag.source_id = tag['tag-source-id'][:255]
                if 'adult' in tag:
                    new_tag.adult = bool(tag['adult'])
                new_tag.save()

                new_tag.from_archiver = self.get_model()
                new_tag.save()

                new_content.tags.add(new_tag)

        new_content.save()

    # returns a preview html string for the content
    @staticmethod
    def make_preview(content_path):
        content_path = pathlib.Path(STATIC_ROOT, content_path)

        if content_path.is_dir():
            for file in content_path.iterdir():
                if file.is_dir():
                    continue
                if file.name == '.metafile':
                    continue

                if file.suffix in image_types:
                    return '<img class=\'preview\' src=\'/' + \
                        str(file).replace(STATIC_ROOT, STATIC_URL).replace('//', '/') + '\'/>'

                if file.suffix in text_types:
                    with open(file, 'r') as in_file:
                        in_lines = in_file.readlines()
                    lines = ''
                    for line in in_lines:
                        lines += line.replace('\n', '') + ' '
                    lines = BeautifulSoup(lines, "lxml").text
                    lines = lines.encode('ascii', errors='ignore').decode()
                    lines = lines.replace('   ', ' ')
                    if len(lines) > 512:
                        lines = lines[:-3] + '...'

                    preview = lines
                    preview = '<p class=\'preview\'>' + str(preview) + '</p>'
                    return preview[:512]

            return '<p class=\'preview\'>This content has no generated preview</p>'
        else:
            return '<p class=\'preview\'>This content has no generated preview</p>'

    # returns 0 if successful, 1 if error
    @staticmethod
    def download(url, filename):
        if url is None or filename is None:
            return 1

        for parent_directory in reversed(pathlib.Path(filename).parents):
            if not parent_directory.exists():
                parent_directory.mkdir()

        file_exists = pathlib.Path(filename).exists()

        if not file_exists:
            r = requests.get(url, stream=True, allow_redirects=True)

            if r.status_code == 200:
                start_time = time.time()

                with open(filename, 'wb') as file:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)

                        if time.time() - start_time >= 600:
                            return 1

                # if the remote server file is not the same size as the local file is, return error
                if int(r.headers.get('content-length', None)) != pathlib.Path(filename).stat().st_size:
                    return 1

        return 0

    @staticmethod
    def validate_url(url):
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            return False
        return True

    def log_print(self, message):
        log_path = pathlib.Path(STATIC_ROOT, self.codename)

        log_path.mkdir(parents=True, exist_ok=True)
        for parent_directory in reversed(pathlib.Path(log_path).parents):
            parent_directory.mkdir(exist_ok=True, mode=0o777)

        log_path = log_path / 'log.txt'

        if not log_path.exists():
            log_path.touch()

        with log_path.open(mode='a') as log_file:
            log_file.write(message + '\n')


def check_metadata(metadata):
    try:
        jsonschema.validate(instance=metadata, schema=metadata_schema)
    except jsonschema.exceptions.ValidationError as err:
        return False, err
    return True

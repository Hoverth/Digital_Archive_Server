import os
import re
import sys
import time
import datetime
import pathlib
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import lxml

from celery import shared_task
from django import forms

from . import ArchiveWorker
from ..settings import STATIC_ROOT, STATIC_URL


# This Generic Archive Worker is provided as an example of how to make an archive worker.
# This requires bs4, requests and lxml


class GenericArchiveWorker(ArchiveWorker.ArchiveWorker):
    # class information
    name = 'Generic Archive Worker'
    codename = 'generic'
    about = 'Archive Worker for generic webpages, files and websites'

    enabled_actions = [
        'get_file',
        'get_webpage'
    ]

    # passes the actions to a local method, as celery (the task manager)
    # does not like class instances in method arguments
    def handle_actions(self, action, data):
        handle_actions.delay(action, data)  # action is a string (the first in the ENABLED_ACTIONS tuple)
        # and data is the cleaned data from the form

    # overloads for the ArchiveWorker webpage form
    class ActionForm(forms.Form):
        ENABLED_ACTIONS = [
            ('get_file', 'Get File'),
            ('get_webpage', 'Get Webpage')
        ]

        action_to_do = forms.ChoiceField(choices=ENABLED_ACTIONS)
        url = forms.URLField(required=False)


# repeat of the class info, just for ease of access
name = 'Generic Archive Worker'
codename = 'generic'
about = 'Archive Worker for generic webpages, files and websites'

enabled_actions = [
    'get_file',
    'get_webpage'
]


# this is the method that gets passed to celery for async processing
# it takes in an action string, and the form data
@shared_task
def handle_actions(action, data):
    if 'url' in data:
        error_message = ''
        if action == 'get_file':
            get_file(data['url'])
        if action == 'get_webpage':
            get_webpage(data['url'])
    else:
        error_message = 'A url needs to be inputted for this operation!'


# this method downloads a webpage, with all it's assets
def get_webpage(url):
    response = requests.get(url, headers={'accept': 'text/html'})

    if response.status_code != 200:
        return False

    dns_address = urlparse(url).netloc

    content_path = pathlib.Path(dns_address, 'webpage', str('/'.join(url.split('/')[3:])))

    complete_path = pathlib.Path(STATIC_ROOT, content_path)
    complete_path.mkdir(parents=True, exist_ok=True)
    for parent_directory in reversed(pathlib.Path(complete_path).parents):
        parent_directory.mkdir(exist_ok=True, mode=0o777)

    page_path = str(complete_path)

    # code adapted using imbr's answer to:
    # https://stackoverflow.com/questions/1825438/download-html-page-and-its-contents/62207356#62207356
    def save_and_rename(soup, pagefolder, session, url, tag, inner):
        if not os.path.exists(pagefolder):  # create only once
            os.mkdir(pagefolder)

        for a_tag in soup.findAll(tag):  # images, css, etc..
            if a_tag.has_attr(inner):  # check inner tag (file object) MUST exist
                try:
                    filename, ext = os.path.splitext(os.path.basename(a_tag[inner]))  # get name and extension
                    filename = re.sub('\W+', '', filename) + ext  # clean special chars from name
                    file_url = urljoin(url, a_tag.get(inner))
                    filepath = pathlib.Path(pagefolder, filename)
                    # rename html ref so can move html and folder of files anywhere
                    a_tag[inner] = '/' + str(pathlib.Path(pagefolder, filename)).replace(STATIC_ROOT,
                                                                                         STATIC_URL).replace('//', '/')
                    if not os.path.isfile(filepath):  # was not downloaded
                        with open(filepath, 'wb') as file:
                            file_binary = session.get(file_url)
                            file.write(file_binary.content)
                except Exception as exc:
                    print(exc, file=sys.stderr)

    session = requests.Session()
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    path, _ = os.path.splitext(page_path)
    page_folder = path  # page contents folder
    tags_inner = {'img': 'src', 'link': 'href', 'script': 'src'}  # tag&inner tags to grab
    for tag, inner in tags_inner.items():  # saves resource files and rename refs
        save_and_rename(soup, page_folder, session, url, tag, inner)

    with open(str(complete_path / 'index.html'), 'w') as file:  # saves modified html doc
        file.write(str(soup))

    GenericArchiveWorker().save_content(
        {
            'title': soup.find('title').text,
            'content-type': dns_address + '/webpage',
            'source-url': url,
            'source-id': '/'.join(url.split('/')[3:]),
            'tags': [{
                'tag-name': 'Generic Webpage',
                'tag-id': dns_address + '/webpage',
            }],
            'creators': [{
                'creator-name': dns_address,
                'creator-id': dns_address + '/creator',
                'creator-source-url': '/'.join(url.split('/')[:3])
            }],
            'content-path': str(content_path),
            'time-retrieved': datetime.datetime.utcnow().isoformat()
        }
    )

    GenericArchiveWorker().log_print(
        'Gotten Webpage ' + url + ' from ' + dns_address + ' by ' + name + ' \nArchival Complete! \n')

    time.sleep(1)

    return True


# this method downloads a file
def get_file(url):
    if not GenericArchiveWorker().validate_url(url):
        return False

    dns_address = urlparse(url).netloc

    filename = pathlib.Path(url).name

    content_path = pathlib.Path(dns_address, 'file')

    complete_path = pathlib.Path(STATIC_ROOT, content_path)
    complete_path.mkdir(parents=True, exist_ok=True)
    for parent_directory in reversed(pathlib.Path(complete_path).parents):
        parent_directory.mkdir(exist_ok=True, mode=0o777)

    full_file_path = complete_path / filename

    GenericArchiveWorker().download(url, full_file_path)

    source_id = '/'.join(url.split('/')[3:])

    GenericArchiveWorker().save_content(
        {
            'title': filename,
            'content-type': dns_address + '/file',
            'source-url': url,
            'source-id': source_id,
            'tags': [{
                'tag-name': 'Generic File',
                'tag-id': dns_address + '/file',
            }],
            'creators': [{
                'creator-name': dns_address,
                'creator-id': dns_address + '/creator',
                'creator-source-url': '/'.join(url.split('/')[:3])
            }],
            'content-path': str(content_path),
            'time-retrieved': datetime.datetime.utcnow().isoformat()
        }
    )

    GenericArchiveWorker().log_print(
        'Gotten file ' + url + ' from ' + dns_address + ' by ' + name + ' \nArchival Complete! \n')

    # wait a certain amount of time before scraping again; sleep for 1 second(s)
    time.sleep(1)
    return True

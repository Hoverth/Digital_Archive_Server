import os
import pathlib

import django.contrib.auth.models
from .models import Creator, Tag, Content, Collection
from .settings import STATIC_ROOT
from django.views import generic


class ContentListView(generic.ListView):
    template_name = 'ContentManager/content-list.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self):
        content_list = Content.objects.order_by('-time_retrieved')
        return content_list


def get_filepath(file_dictionary):
    return file_dictionary['path']


class ContentDetailView(generic.DetailView):
    model = Content
    template_name = 'ContentManager/content-details.html'
    context_object_name = 'content'

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)

        content = context['content']
        if self.request.user.is_authenticated:
            content.seen_by.add(self.request.user)
            content.save()

        image_types = ['.gif', '.jpg', '.png']
        video_types = ['.mp4', '.mkv']
        text_types = ['.txt']
        iframe_types = ['.html']

        files = []
        if pathlib.Path(STATIC_ROOT, content.content_path).is_dir():
            for file in pathlib.Path(STATIC_ROOT, content.content_path).glob('*'):
                if '.meta' in file.name:
                    continue
                file_out = {
                    'type': '',
                    'path': str(pathlib.Path(content.content_path, file)).replace(STATIC_ROOT, ''),
                    'content': None
                }
                file_extension = pathlib.Path(str(file)).suffix.lower()
                if file_extension in image_types:
                    file_out['type'] = 'image'

                if file_extension in video_types:
                    file_out['type'] = 'video'

                if file_extension in iframe_types:
                    file_out['type'] = 'iframe'

                if file_extension in text_types:
                    file_out['type'] = 'text'
                    contents = ''
                    try:
                        with open(pathlib.Path(STATIC_ROOT, content.content_path, file), 'r') as infile:
                            contents = infile.read().replace('\n', '<br>')
                    except:
                        contents = 'Error Reading Text File: ' + str(file)
                    file_out['contents'] = str(contents)

                files.append(file_out)
        files.sort(key=get_filepath)
        context['files'] = files

        return context


class TagsListView(generic.ListView):
    template_name = 'ContentManager/tags.html'
    context_object_name = 'tag_list'
    paginate_by = 20

    def get_queryset(self):
        tag_list = Tag.objects.order_by('name')
        return tag_list


class TagDetailsView(generic.ListView):
    template_name = 'ContentManager/tag.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(tags__id=self.kwargs['pk']).order_by('-time_retrieved')
        return content_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagDetailsView, self).get_context_data(**kwargs)
        context['tag'] = Tag.objects.filter(id=self.kwargs['pk']).first()
        return context


class NoTagsDetailsView(generic.ListView):
    template_name = 'ContentManager/notag.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(tags=None).order_by('-time_retrieved')
        return content_list


class CreatorsListView(generic.ListView):
    template_name = 'ContentManager/creators.html'
    context_object_name = 'creator_list'
    paginate_by = 20

    def get_queryset(self):
        creator_list = Creator.objects.order_by('name')
        return creator_list


class CreatorDetailsView(generic.ListView):
    template_name = 'ContentManager/creator.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(creators__id=self.kwargs['pk']).order_by('-time_retrieved')
        return content_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreatorDetailsView, self).get_context_data(**kwargs)
        context['creator'] = Creator.objects.filter(id=self.kwargs['pk']).first()
        return context


class NoCreatorsDetailsView(generic.ListView):
    template_name = 'ContentManager/nocreator.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(creators=None).order_by('-time_retrieved')
        return content_list


class CollectionsListView(generic.ListView):
    template_name = 'ContentManager/collections.html'
    context_object_name = 'collection_list'
    paginate_by = 20

    def get_queryset(self):
        collection_list = Collection.objects.order_by('name')
        return collection_list


class CollectionDetailsView(generic.ListView):
    template_name = 'ContentManager/collection.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(tags__id=self.kwargs['pk']).order_by('-time_retrieved')
        return content_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CollectionDetailsView, self).get_context_data(**kwargs)
        context['collection'] = Collection.objects.filter(id=self.kwargs['pk']).first()
        return context


class NoCollectionsDetailsView(generic.ListView):
    template_name = 'ContentManager/nocollection.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(collection_content=None).order_by('-time_retrieved')
        return content_list

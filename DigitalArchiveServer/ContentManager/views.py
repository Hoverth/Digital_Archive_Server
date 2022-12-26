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
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            content_list = content_list.exclude(tags__tag_id='adult-content')
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

        if Tag.objects.filter(tag_id='adult-content').exists():
            adult_content_tag = Tag.objects.get(tag_id='adult-content')
        else:
            context['content'] = None
            return context

        if (not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content')) \
                and adult_content_tag not in content.tags:
            context['content'] = None
            return context

        if self.request.user.is_authenticated:
            content.seen_by.add(self.request.user)
            content.save()

            if self.request.GET:
                if 'like' in self.request.GET:
                    content.liked_by.add(self.request.user)
                    content.save()

        image_types = ['.gif', '.jpg', '.png']
        video_types = ['.mp4', '.mkv']
        text_types = ['.txt']
        iframe_types = ['.html', '.pdf']
        ignore_types = ['.vtt']

        files = []
        other_files = []
        if pathlib.Path(STATIC_ROOT, content.content_path).is_dir():
            for file in pathlib.Path(STATIC_ROOT, content.content_path).glob('*'):
                if '.meta' in file.name or '.thumbnail-' in file.name:
                    continue

                file_out = {
                    'type': '',
                    'path': str(pathlib.Path(content.content_path, file)).replace(STATIC_ROOT, '').strip('/'),
                    'content': None
                }
                file_extension = pathlib.Path(str(file)).suffix.lower()

                if file_extension in ignore_types:
                    continue

                if file_extension in image_types:
                    file_out['type'] = 'image'
                elif file_extension in video_types:
                    file_out['type'] = 'video'
                elif file_extension in iframe_types:
                    file_out['type'] = 'iframe'
                elif file_extension in text_types:
                    file_out['type'] = 'text'
                    contents = ''
                    try:
                        with open(pathlib.Path(STATIC_ROOT, content.content_path, file), 'r') as infile:
                            contents = infile.read().replace('\n', '<br>')
                    except:
                        contents = 'Error Reading Text File: ' + str(file)
                    file_out['contents'] = str(contents)
                else:
                    other_files.append(file_out)
                    continue
                files.append(file_out)
        files.sort(key=get_filepath)
        if other_files is not None:
            other_files.sort(key=get_filepath)
            files += other_files
        context['files'] = files

        return context


class TagsListView(generic.ListView):
    template_name = 'ContentManager/tags.html'
    context_object_name = 'tag_list'
    paginate_by = 20

    def get_queryset(self):
        tag_list = Tag.objects.order_by('name')
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            tag_list = tag_list.exclude(adult=True)

        return tag_list


class TagDetailsView(generic.ListView):
    template_name = 'ContentManager/tag.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(tags__id=self.kwargs['pk']).order_by('-time_retrieved')
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            content_list = content_list.exclude(tags__tag_id='adult-content')

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
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            content_list = content_list.exclude(tags__tag_id='adult-content')

        return content_list


class CreatorsListView(generic.ListView):
    template_name = 'ContentManager/creators.html'
    context_object_name = 'creator_list'
    paginate_by = 20

    def get_queryset(self):
        creator_list = Creator.objects.order_by('name')
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            creator_list = creator_list.exclude(adult=True)
        return creator_list


class CreatorDetailsView(generic.ListView):
    template_name = 'ContentManager/creator.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(creators__id=self.kwargs['pk']).order_by('-time_retrieved')
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            content_list = content_list.exclude(tags__tag_id='adult-content')

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
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            content_list = content_list.exclude(tags__tag_id='adult-content')

        return content_list


class CollectionsListView(generic.ListView):
    template_name = 'ContentManager/collections.html'
    context_object_name = 'collection_list'
    paginate_by = 20

    def get_queryset(self):
        collection_list = Collection.objects.order_by('name')
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            collection_list = collection_list.exclude(adult=True)
        return collection_list


class CollectionDetailsView(generic.ListView):
    template_name = 'ContentManager/collection.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(tags__id=self.kwargs['pk']).order_by('-time_retrieved')
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            content_list = content_list.exclude(tags__tag_id='adult-content')

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
        if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
            content_list = content_list.exclude(tags__tag_id='adult-content')
        
        return content_list

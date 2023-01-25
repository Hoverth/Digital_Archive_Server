import operator
from functools import reduce

from django import forms
from django.db.models import Q
from django.views import generic

from .models import Content, Collection


def get_content_from_search(search):
    q_list = []

    title = search['title']
    if title != '':
        q_list.append(Q(title__icontains=title))

    content_type = search['content_type']
    if content_type != '':
        q_list.append(Q(content_type__icontains=content_type))

    source_url = search['source_url']
    if source_url != '':
        q_list.append(Q(source_url__icontains=source_url))

    source_id = search['source_id']
    if source_id != '':
        q_list.append(Q(source_id__icontains=source_id))

    content_path = search['content_path']
    if content_path != '':
        q_list.append(Q(content_path__icontains=content_path))

    notes = search['notes']
    if notes != '':
        q_list.append(Q(notes__icontains=notes))

    language = search['language']
    if language != '':
        q_list.append(Q(language__icontains=language))

    copyright = search['copyright']
    if copyright != '':
        q_list.append(Q(copyright=copyright))

    time_created_start = search['time_created_start']
    time_created_end = search['time_created_end']
    time_retrieved_start = search['time_retrieved_start']
    time_retrieved_end = search['time_retrieved_end']
    published_date_start = search['published_date_start']
    published_date_end = search['published_date_end']

    content_size = search['content_size']

    from_archiver = search['from_archiver']
    if from_archiver != '':
        q_list.append(Q(from_archiver__name__icontains=from_archiver))

    creator_names = search['creator_names']
    if from_archiver != '':
        q_list.append(Q(creators__name__icontains=creator_names))

    tag_names = search['tag_names']
    if from_archiver != '':
        q_list.append(Q(tags__name__icontains=tag_names))

    if content_size is not None:
        q_list.append(Q(content_size__gt=(content_size - 50)) & Q(content_size__lt=(content_size + 50)))

    if time_created_start is not None and time_created_end is not None:
        q_list.append(Q(time_retrieved__range=(time_created_start, time_created_end)))

    if time_retrieved_start is not None and time_retrieved_end is not None:
        q_list.append(Q(time_retrieved__range=(time_retrieved_start, time_retrieved_end)))

    if published_date_start is not None and published_date_end is not None:
        q_list.append(Q(time_retrieved__range=(published_date_start, published_date_end)))

    order_by = '-time_retrieved'
    if search['order_by'] != '':
        order_by = search['order_by']

    if q_list:
        content_list = Content.objects.filter(reduce(operator.and_, q_list)).distinct().order_by(order_by)
    else:
        content_list = Content.objects.all().order_by(order_by)

    return content_list


class CollectionCreationForm(forms.Form):
    name = forms.CharField(max_length=255, required=False)
    restricted_access = forms.BooleanField(required=False)
    adult = forms.BooleanField(required=False)


class SearchForm(forms.Form):
    ORDER_BY = [
        ('-time_retrieved', 'Time Retrieved (Descending)'),
        ('time_retrieved', 'Time Retrieved (Ascending)'),
        ('-published_date', 'Published Date (Descending)'),
        ('published_date', 'Published Date (Ascending)'),
        ('?', 'Random'),
        ('title', 'Title (Ascending)'),
        ('-title', 'Title (Descending)'),
        ('source_url', 'Source Url (Ascending)'),
        ('-source_url', 'Source Url (Descending)'),
        ('content_path', 'Content Path (Ascending)'),
        ('-content_path', 'Content Path (Descending)'),
        ('content_type', 'Content Type (Ascending)'),
        ('-content_type', 'Content Type (Descending)')
    ]

    title = forms.CharField(required=False)
    content_type = forms.CharField(required=False)
    source_url = forms.CharField(required=False)
    source_id = forms.CharField(required=False)
    content_path = forms.CharField(required=False)
    notes = forms.CharField(required=False)
    language = forms.CharField(required=False)
    copyright = forms.CharField(required=False)

    time_created_start = forms.DateTimeField(required=False)
    time_created_end = forms.DateTimeField(required=False)
    time_retrieved_start = forms.DateTimeField(required=False)
    time_retrieved_end = forms.DateTimeField(required=False)
    published_date_start = forms.DateTimeField(required=False)
    published_date_end = forms.DateTimeField(required=False)

    content_size = forms.IntegerField(min_value=0, required=False)

    from_archiver = forms.CharField(required=False)
    creator_names = forms.CharField(required=False)
    tag_names = forms.CharField(required=False)

    order_by = forms.ChoiceField(choices=ORDER_BY, initial=1, required=False)


class SearchView(generic.ListView):
    template_name = 'ContentManager/search.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self):
        if self.request.method == 'GET':
            form = SearchForm(self.request.GET)
            if form.is_valid():
                content_list = get_content_from_search(form.cleaned_data)

                if not self.request.user.is_authenticated or not self.request.user.has_perm('ContentManager.adult_content'):
                    content_list = content_list.exclude(tags__tag_id='adult-content')
            else:
                content_list = []
            return content_list
        return []

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        if self.request.method == 'GET':
            form = SearchForm(self.request.GET)
        else:
            form = SearchForm()

        if self.request.method == 'GET':
            collection_form = CollectionCreationForm(self.request.GET)
        else:
            collection_form = CollectionCreationForm()

        if collection_form.is_valid() and form.is_valid():
            if collection_form.cleaned_data['name'] != '':
                c = Collection()
                c.name = collection_form.cleaned_data['name']

                if collection_form.cleaned_data['restricted_access'] is not None:
                    c.restricted_access = collection_form.cleaned_data['restricted_access']
                else:
                    c.restricted_access = False

                if collection_form.cleaned_data['adult'] is not None:
                    c.adult = collection_form.cleaned_data['adult']
                else:
                    c.adult = False

                c.search = form.cleaned_data

                preview_content_list = get_content_from_search(form.cleaned_data)
                if not collection_form.cleaned_data['adult']:
                    preview_content = preview_content_list.exclude(tags__tag_id='adult-content').first()
                    c.preview = preview_content.preview
                else:
                    preview_content = preview_content_list.first()
                    c.preview = preview_content.preview

                c.save()

                c.can_access.add(self.request.user)
                c.owners.add(self.request.user)

        context['collection_form'] = collection_form
        context['form'] = form

        return context



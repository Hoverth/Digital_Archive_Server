from django import forms
from django.db.models import Q
from django.views import generic

from .models import Content


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
                print(form.cleaned_data)
                title = form.cleaned_data['title']
                content_type = form.cleaned_data['content_type']
                source_url = form.cleaned_data['source_url']
                source_id = form.cleaned_data['source_id']
                content_path = form.cleaned_data['content_path']
                notes = form.cleaned_data['notes']
                language = form.cleaned_data['language']
                copyright = form.cleaned_data['copyright']

                time_created_start = form.cleaned_data['time_created_start']
                time_created_end = form.cleaned_data['time_created_end']
                time_retrieved_start = form.cleaned_data['time_retrieved_start']
                time_retrieved_end = form.cleaned_data['time_retrieved_end']
                published_date_start = form.cleaned_data['published_date_start']
                published_date_end = form.cleaned_data['published_date_end']

                content_size = form.cleaned_data['content_size']

                from_archiver = form.cleaned_data['from_archiver']
                creator_names = form.cleaned_data['creator_names']
                tag_names = form.cleaned_data['tag_names']

                if content_size is not None:
                    content_filter = Q(content_size__gt=(content_size - 50)) & Q(content_size__lt=(content_size + 50))
                else:
                    content_filter = Q()

                if time_created_start is not None and time_created_end is not None:
                    time_created_filter = Q(time_retrieved__range=(time_created_start, time_created_end))
                else:
                    time_created_filter = Q()

                if time_retrieved_start is not None and time_retrieved_end is not None:
                    time_retrieved_filter = Q(time_retrieved__range=(time_retrieved_start, time_retrieved_end))
                else:
                    time_retrieved_filter = Q()

                if published_date_start is not None and published_date_end is not None:
                    published_date_filter = Q(time_retrieved__range=(published_date_start, published_date_end))
                else:
                    published_date_filter = Q()

                order_by = '-time_retrieved'
                if form.cleaned_data['order_by'] != '':
                    order_by = form.cleaned_data['order_by']
                print(order_by)

                content_list = Content.objects.filter(
                    Q(title__icontains=title) &
                    Q(content_type__icontains=content_type) &
                    Q(source_url__icontains=source_url) &
                    Q(source_id__icontains=source_id) &
                    Q(content_path__icontains=content_path) &
                    Q(notes__icontains=notes) &
                    Q(language__icontains=language) &
                    Q(copyright__icontains=copyright) &

                    time_created_filter &
                    time_retrieved_filter &
                    published_date_filter &

                    content_filter &

                    Q(from_archiver__name__icontains=from_archiver) &
                    Q(creators__name__icontains=creator_names) &
                    Q(tags__name__icontains=tag_names)
                ).distinct().order_by(order_by)

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

        context['form'] = form

        return context

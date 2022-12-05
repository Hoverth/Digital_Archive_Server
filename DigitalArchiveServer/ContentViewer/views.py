from django.shortcuts import render
from .models import Creator, Tag, Content, Collection
from django.views import generic


class ContentListView(generic.ListView):
    template_name = 'ContentViewer/list.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self):
        content_list = Content.objects.order_by('-time_retrieved')
        return content_list


class ContentDetailView(generic.DetailView):
    model = Content
    template_name = 'ContentViewer/details.html'
    context_object_name = 'content'

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)

        content = context['content']
        content.seen_by.add(self.request.user)
        content.save()

        return context
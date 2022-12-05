from django.shortcuts import render
from .models import Creator, Tag, Content, Collection
from django.views import generic


class ContentListView(generic.ListView):
    template_name = 'ContentViewer/content-list.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self):
        content_list = Content.objects.order_by('-time_retrieved')
        return content_list


class ContentDetailView(generic.DetailView):
    model = Content
    template_name = 'ContentViewer/content-details.html'
    context_object_name = 'content'

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)

        content = context['content']
        content.seen_by.add(self.request.user)
        content.save()

        return context


class TagView(generic.ListView):
    template_name = 'ContentViewer/tag.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(tags__id=self.kwargs['pk']).order_by('-time_retrieved')
        return content_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context['tag'] = Tag.objects.filter(id=self.kwargs['pk']).first()
        return context


class CreatorView(generic.ListView):
    template_name = 'ContentViewer/creator.html'
    context_object_name = 'content_list'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        content_list = Content.objects.filter(creators__id=self.kwargs['pk']).order_by('-time_retrieved')
        return content_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CreatorView, self).get_context_data(**kwargs)
        context['creator'] = Creator.objects.filter(id=self.kwargs['pk']).first()
        return context

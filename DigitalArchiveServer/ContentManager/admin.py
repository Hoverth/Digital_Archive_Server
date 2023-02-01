from django.contrib import admin

from .models import Creator, Tag, Content, Collection, Archiver


class ContentAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'title', 'source_url']
    list_filter = ['published_date', 'tags']

    actions = ['make_adult']


admin.site.register(Tag)
admin.site.register(Creator)
admin.site.register(Content, ContentAdmin)
admin.site.register(Collection)
admin.site.register(Archiver)

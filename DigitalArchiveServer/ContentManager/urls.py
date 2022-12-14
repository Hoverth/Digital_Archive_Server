from django.urls import path, include
from . import views


app_name = "ContentManager"  # {{ url }} needs to have "main:" before the urls name
urlpatterns = [
    path('', views.ContentListView.as_view(), name='index'),
    path('content/<int:pk>', views.ContentDetailView.as_view(), name='content'),
    path('tags', views.TagsListView.as_view(), name='tags'),
    path('tag/0', views.NoTagsDetailsView.as_view(), name='notag'),
    path('tag/<int:pk>', views.TagDetailsView.as_view(), name='tag'),
    path('creators', views.CreatorsListView.as_view(), name='creators'),
    path('creator/0', views.NoCreatorsDetailsView.as_view(), name='nocreator'),
    path('creator/<int:pk>', views.CreatorDetailsView.as_view(), name='creator'),
    path('collections', views.CollectionsListView.as_view(), name='collections'),
    path('collection/0', views.NoCollectionsDetailsView.as_view(), name='nocollection'),
    path('collection/<int:pk>', views.CollectionDetailsView.as_view(), name='collection'),
    path('archivers/', include('ContentManager.Archivers.archiver'))
]
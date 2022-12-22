from django.urls import path, include
from . import views, user_views
from .search import SearchView


app_name = "ContentManager"  # {{ url }} needs to have "ContentManager:" before the urls name
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
    path('search', SearchView.as_view(), name='search'),

    path('archivers/', include('ContentManager.Archivers.archiver')),

    path('user/<str:username>', user_views.user_view, name='user'),
    path('user/<str:username>/seen', user_views.user_seen_view, name='user_seen'),
    path('user/<str:username>/liked', user_views.user_liked_view, name='user_liked'),
    path('user/<str:username>/collections', user_views.user_collections_view, name='user_collections')
]
from django.urls import path, include
from . import views


app_name = "ContentViewer"  # {{ url }} needs to have "main:" before the urls name
urlpatterns = [
    path('', views.ContentListView.as_view(), name='index'),
    path('content/<int:pk>', views.ContentDetailView.as_view(), name='content'),
    path('tag/<int:pk>', views.TagView.as_view(), name='tag'),
    path('creator/<int:pk>', views.CreatorView.as_view(), name='creator'),
]
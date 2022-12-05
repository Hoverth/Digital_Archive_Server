from django.urls import path, include
from . import views


app_name = "ContentViewer"  # {{ url }} needs to have "main:" before the urls name
urlpatterns = [
    path('', views.ContentListView.as_view(), name='index'),
    path('content/<int:pk>', views.ContentDetailView.as_view(), name='content'),
]
from django.urls import path
from .views import article_list,article_detail

urlpatterns = [
    path('start', article_list),
    # path('download/<str:type>/<str:roomid>', article_detail),
]
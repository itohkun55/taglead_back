from django.urls import path
from django.views.generic import TemplateView
from .views import (
    IndexView,
    InsertNewUserView
)
urlpatterns = [
    path('', IndexView.as_view(template_name="index.html"),name="index"),
    path('insert', InsertNewUserView.as_view(template_name="insertUser.html"),name="insert"),
     ]

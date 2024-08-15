from django.urls import path
from . import views

urlpatterns = [
    path('', views.convert_code, name="convert_code"),
]

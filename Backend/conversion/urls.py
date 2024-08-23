from django.urls import path
from . import views

urlpatterns = [
    path('', views.convert_code, name="convert_code"),
    path('accuracy', views.accuracy, name="convert_code"),
]

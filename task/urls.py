from django.urls import path

from task import views

urlpatterns = [
    path('launch', views.launch),
    path('get_result', views.get_result)
]
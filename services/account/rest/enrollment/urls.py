from django.urls import path
from .views import CreateView


app_name = "enrollment"


urlpatterns = [
    path('', CreateView.as_view(), name='create'),
]

from django.urls import path
from .views import CreateView


app_name = "account"


urlpatterns = [
    path('<slug:subid>/', CreateView.as_view(), name='create'),
]

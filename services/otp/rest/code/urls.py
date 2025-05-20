from django.urls import path
from .views import CodeView


app_name = "code"


urlpatterns = [
    path('<slug:subid>/', CodeView.as_view(), name='sign'),
]

from django.urls import path
from .views import EnrollmentView, CreateView


app_name = "email"


urlpatterns = [
    path('', CreateView.as_view(), name='create'),
    path('old/', EnrollmentView.as_view(), name='register'),
]

from django.urls import path
from .views import ask_endpoint

urlpatterns = [
    path('ask/', ask_endpoint, name='ask_question'),
]

from django.views.generic import TemplateView
from django.urls import path
from . import views

# URLConfig
urlpatterns = [
    path("", TemplateView.as_view(template_name="core/index.html")),
]

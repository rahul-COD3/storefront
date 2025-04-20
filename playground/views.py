from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import requests


class HelloView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        result = requests.get("https://httpbin.org/delay/2")
        return render(request, "hello.html", {"name": result.json()})

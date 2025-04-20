from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
import requests
import logging

logger = logging.getLogger(__name__)


class HelloView(APIView):
    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        try:
            logger.info("Fetching data from httpbin")
            result = requests.get("https://httpbin.org/delay/2")
            logger.info("Data fetched successfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
        return render(request, "hello.html", {"name": result.json()})

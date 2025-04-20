from django.core.mail import EmailMessage, BadHeaderError
from django.shortcuts import render
from templated_mail.mail import BaseEmailMessage
from .tasks import notify_customer
import requests


def say_hello(request):
    requests.get("https://httpbin.org/delay/2")
    return render(request, "hello.html", {"name": "Rahul"})

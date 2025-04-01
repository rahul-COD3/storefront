from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
# request -> response
# request handler
# action

def calculate():
    x = 1
    y = 2
    return x + y


def say_hello(request):
    x = calculate()
    return render(request, 'hello.html', {'name': 'John'})
    
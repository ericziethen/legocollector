from django.http import HttpResponse
# from django.shortcuts import render


# Create your views here.
def index(request):  # pylint: disable=unused-argument
    return HttpResponse('Inventory Main Page - Placeholder')

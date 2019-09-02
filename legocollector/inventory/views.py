from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# from django.shortcuts import render


# Create your views here.
@login_required
def index(request):  # pylint: disable=unused-argument
    # user = request.user
    return HttpResponse('Inventory Main Page - Placeholder')

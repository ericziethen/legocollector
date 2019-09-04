from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView

from .models import UserPart

# Create your views here.


@login_required
def index(request):  # pylint: disable=unused-argument
    # user = request.user
    return HttpResponse('Inventory Main Page - Placeholder')


class UserPartList(LoginRequiredMixin, ListView):  # pylint: disable=too-many-ancestors
    model = UserPart

    def get_queryset(self):
        """Only for current user."""
        return UserPart.objects.filter(user_id=self.request.user)

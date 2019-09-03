from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import ListView

from .models import UserPart, Color

# Create your views here.

# TODO - DO WE NEED DEFAULT INDEX VIEW STILL ???
@login_required
def index(request):  # pylint: disable=unused-argument
    # user = request.user
    return HttpResponse('Inventory Main Page - Placeholder')


class UserPartList(LoginRequiredMixin, ListView):
    model = UserPart

    def get_queryset(self):
        """Only for current user."""
        return UserPart.objects.filter(user_id=self.request.user)

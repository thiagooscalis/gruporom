from django.urls import path
from core.views.base import RedirectToGroupView

urlpatterns = [
    path('', RedirectToGroupView.as_view(), name='redirect_to_group'),
]
from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Votings

def index(request):
    return render(request, 'dashboard/dashboard.html', {})


def detail(request):
    all_votings = Votings.objects.all()
    return render(request, 'dashboard/detail.html', {'all_objects':all_votings})

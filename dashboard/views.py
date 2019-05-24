from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Votings, Individual_votings


def index(request):
    return render(request, 'dashboard/index.html', {})


def list(request):
    all_votings = Votings.objects.all()
    print(all_votings)
    return render(request, 'dashboard/list.html', {'all_objects': all_votings})


def detail(request, voting_id):
    voting_parties = Individual_votings.objects.filter(voting_id=voting_id)
    print(voting_parties)
    return render(request, 'dashboard/detail.html', {'abc': voting_parties})

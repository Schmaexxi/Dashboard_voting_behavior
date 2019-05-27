from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Votings, Individual_votings


def index(request):
    return render(request, 'dashboard/index.html', {})


def list(request):
    all_votings = Votings.objects.all()
    return render(request, 'dashboard/list.html', {'all_objects': all_votings})


def detail(request, voting_id):
    voting_parties = Individual_votings.objects.filter(voting_id=voting_id)[0]
    print(voting_parties.voting)
    # only works if first value is not an empty list
    b = [key for key in voting_parties.voting[[k for k in voting_parties.voting.keys()][0]][0].keys()]
    specific_voting = Votings.objects.filter(voting_id=voting_id)[0]
    return render(request, 'dashboard/detail.html', {'all_factions': voting_parties,
                                                     "specific_voting": specific_voting,
                                                     "attributes": b})

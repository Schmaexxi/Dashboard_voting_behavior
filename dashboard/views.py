from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Voting, IndividualVoting


def index(request):
    #voting_behavior = IndividualVoting.objects.filter(voting__SPD__contains=[{'name': 'Annen'}])
    #print(voting_behavior)
    return render(request, 'dashboard/index.html', {})


def list(request):
    all_votings = Voting.objects.all().order_by("voting_id")
    print(all_votings)
    return render(request, 'dashboard/list.html', {'all_votings': all_votings})


def detail(request, voting_id):
    voting_parties = IndividualVoting.objects.filter(voting_id=voting_id)[0]
    # only works if first value is not an empty list
    b = [key for key in voting_parties.voting[[k for k in voting_parties.voting.keys()][0]][0].keys()]
    all_votings = Voting.objects.all()
    specific_voting = all_votings.filter(voting_id=voting_id)[0]
    votes = [int(n) for n in specific_voting.json['votes'].values()]
    return render(request, 'dashboard/detail.html', {'all_factions': voting_parties,
                                                     'all_votings': all_votings,
                                                     "specific_voting": specific_voting,
                                                     "vote_labels": [lbl for lbl in specific_voting.json['votes'].keys()],
                                                     "votes": votes,
                                                     "attributes": b})

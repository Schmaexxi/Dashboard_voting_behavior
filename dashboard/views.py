from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Voting, IndividualVoting, Politician


def index(request):
    #voting_behavior = IndividualVoting.objects.filter(voting__SPD__contains=[{'name': 'Annen'}])
    #print(voting_behavior)
    return render(request, 'dashboard/index.html', {})


def list(request):
    all_votings = Voting.objects.all().order_by("voting_id")
    return render(request, 'dashboard/list.html', {'all_votings': all_votings})


def detail(request, voting_id):
    voting_parties = Voting.objects.filter(voting_id=voting_id)[0]
    politicians = Voting.objects.get(voting_id=voting_id).politicians.all()
    politician_votes = IndividualVoting.objects.filter(voting_id=voting_id).values_list('vote', flat=True)
    print(politician_votes)
    vote_labels = [key for key in voting_parties.votes.keys()]
    votes = [int(n) for n in voting_parties.votes.values()]
    all_votings = Voting.objects.all()
    factions = politicians.distinct().values_list('faction', flat=True)
    specific_voting = all_votings.filter(voting_id=voting_id)[0]
    return render(request, 'dashboard/detail.html', {'all_factions': factions,
                                                     'politicians': politicians,
                                                     'all_votings': all_votings,
                                                     "specific_voting": specific_voting,
                                                     "votes": votes,
                                                     "vote_labels": vote_labels})

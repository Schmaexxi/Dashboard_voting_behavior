from django.shortcuts import render
from django.http import HttpResponse
from dashboard.models import Voting, IndividualVoting, Politician
import datetime
from dateutil.relativedelta import relativedelta


def index(request):
    date_today = datetime.date.today()
    date_minus_six_months = date_today + relativedelta(months=-6)
    latest_votings = Voting.objects.filter(date__range=(date_minus_six_months, date_today))
    latest_genres = latest_votings.values_list('genre', flat=True)
    votings_count = len(latest_votings)
    genres = {}
    for genre in latest_genres:
        if genres.get(genre) is not None:
            genres[genre] += 1
        else:
            genres[genre] = 0
    genre_counts = [value for value in genres.values()]
    genre_labels = [key for key in genres.keys()]
    return render(request, 'dashboard/index.html', {'number_of_votings': votings_count,
                                                    'genre_labels': genre_labels,
                                                    'genre_counts': genre_counts})


def list(request):
    all_votings = Voting.objects.all().order_by("voting_id")
    return render(request, 'dashboard/list.html', {'all_votings': all_votings})


def detail(request, voting_id):
    voting_parties = Voting.objects.filter(voting_id=voting_id)[0]
    pol_objects = Voting.objects.get(voting_id=voting_id).politicians.all()
    pol_objects.order_by('politician_id')
    pol_votes = IndividualVoting.objects.filter(voting_id=voting_id).order_by('politician_id').values_list('vote', flat=True)
    politicians = tuple(zip(pol_objects, pol_votes))
    factions = pol_objects.distinct().values_list('faction', flat=True)
    vote_labels = [key for key in voting_parties.votes.keys()]
    votes = [int(n) for n in voting_parties.votes.values()]
    specific_voting = Voting.objects.filter(voting_id=voting_id)[0]
    print(Voting.objects.filter(voting_id=voting_id).values_list('date'))
    end_date = datetime.date(2019, 3, 31)
    start_date = datetime.date(2017, 1, 1)
    print(start_date)
    print(end_date)
    print(len(Voting.objects.filter(date__range=(start_date, end_date))))

    return render(request, 'dashboard/detail.html', {'all_factions': factions,
                                                     'politicians': politicians,
                                                     "specific_voting": specific_voting,
                                                     "votes": votes,
                                                     "vote_labels": vote_labels})

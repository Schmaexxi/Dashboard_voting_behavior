from django.shortcuts import render
from dashboard.models import Voting, IndividualVoting, Politician
import datetime
from dateutil.relativedelta import relativedelta


# TODO: show statistics of votings by party - e.g.: cdu  votes x times no y times yes z times ... for these votings
def index(request):
    date_today = datetime.date.today()
    date_minus_six_months = date_today + relativedelta(months=-6)
    latest_votings = Voting.objects.filter(date__range=(date_minus_six_months, date_today))
    votings_count = latest_votings.count()
    voting_ids = [voting.voting_id for voting in latest_votings]

    factions = IndividualVoting.objects.filter(voting_id__in=voting_ids).values_list('politician__faction', flat=True).distinct()
    vote_options = IndividualVoting.objects.values_list('vote',flat=True).distinct()
    a = {vote: 0 for vote in vote_options}
    print(a)
    faction_votes = {key: {'Ja': 0, 'Nein' : 0, 'Enthalten': 0, 'Nicht abg.': 0, 'Nicht abg.(Gesetzlicher Mutterschutz)': 0} for key in factions}

    politician_votes = IndividualVoting.objects.filter(voting_id__in=voting_ids).values_list('politician__faction', 'vote')

    total_votes = {i: IndividualVoting.objects.filter(voting_id__in=voting_ids, vote=i).count() for i in vote_options}
    print(total_votes)

    for i in politician_votes:
        faction_votes[i[0]][i[1]] += 1

    latest_genres = latest_votings.values_list('genre', flat=True)

    # TODO: perform aggregation operation in query
    genres = {}
    for genre in latest_genres:
        if genres.get(genre) is not None:
            genres[genre] += 1
        else:
            genres[genre] = 0

    # TODO: perform filtering operation in query
    # remove genres that did not appear in the designated time span
    genres = {k: v for k, v in genres.items() if v > 0}

    genre_counts = [value for value in genres.values()]
    genre_labels = [key for key in genres.keys()]

    return render(request, 'dashboard/index.html', {'number_of_votings': votings_count,
                                                    'genre_labels': genre_labels,
                                                    'genre_counts': genre_counts,
                                                    'faction_votes': faction_votes})


def list(request):
    all_votings = Voting.objects.all().order_by('date')
    return render(request, 'dashboard/list.html', {'all_votings': all_votings})


def detail(request, voting_id):
    specific_voting = Voting.objects.filter(voting_id=voting_id)[0]
    # get politicians related to this specific voting
    pol_objects = Voting.objects.get(voting_id=voting_id).politicians.all()
    pol_objects.order_by('politician_id')
    # get respective politician's vote - order as previous query!
    pol_votes = IndividualVoting.objects.filter(voting_id=voting_id).order_by('politician_id').values_list('vote', flat=True)
    politicians = tuple(zip(pol_objects, pol_votes))
    factions = pol_objects.distinct().values_list('faction', flat=True)
    vote_labels = [key for key in specific_voting.votes.keys()]
    votes = [int(n) for n in specific_voting.votes.values()]
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

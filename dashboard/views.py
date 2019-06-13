from django.shortcuts import render, HttpResponse
from dashboard.models import Voting, IndividualVoting, Politician
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.utils.timezone import now
from urllib.parse import unquote
from django.views.decorators.http import require_http_methods
from dashboard.forms import DateForm
# TODO: show statistics of votings by party - e.g.: cdu  votes x times no y times yes z times ... for these votings


@require_http_methods(["GET", "POST"])
def index(request):

    date_form = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date = date_form.fields['start_date'].initial
    start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y')
    end_date = date_form.fields['end_date'].initial
    end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y')

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
            print(start_date, end_date)
        else:
            print("data invalid")

    # get votings of last x months
    latest_votings = Voting.objects.filter(date__range=(start_date, end_date))
    votings_count = latest_votings.count()
    voting_ids = [voting.voting_id for voting in latest_votings]

    factions = IndividualVoting.objects.filter(voting_id__in=voting_ids).values_list('politician__faction',
                                                                                     flat=True).distinct()
    print(factions)
    vote_options = IndividualVoting.objects.values_list('vote', flat=True).distinct()
    faction_votes = {key: {vote: 0 for vote in vote_options} for key in factions}
    politician_votes = IndividualVoting.objects.filter(voting_id__in=voting_ids).values_list('politician__faction',
                                                                                             'vote')
    total_votes = {i: IndividualVoting.objects.filter(voting_id__in=voting_ids, vote=i).count() for i in vote_options}

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
                                                    'faction_votes': faction_votes,
                                                    'total_votes': total_votes,
                                                    'start_date': start_date,
                                                    'end_date': end_date,
                                                    'form': date_form})


def list(request):
    all_votings = Voting.objects.all().order_by('date')
    return render(request, 'dashboard/list.html', {'all_votings': all_votings})


def detail(request, voting_id):
    specific_voting = Voting.objects.filter(voting_id=voting_id)[0]
    # get politicians related to this specific voting
    pol_objects = Voting.objects.get(voting_id=voting_id).politicians.all()
    pol_objects.order_by('politician_id')
    # get respective politician's vote - order as previous query!
    pol_votes = IndividualVoting.objects.filter(voting_id=voting_id).order_by('politician_id').values_list('vote',
                                                                                                           flat=True)
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


def genre_votes(request, name):
    cells = IndividualVoting.objects.filter(voting__date__range=(now() + relativedelta(months=-6), now()),
                                            voting__genre=name).values('politician__faction',
                                                                       'vote').annotate(Count('vote'))
    # print(cells)
    objects = {}
    for cell in cells:
        objects.setdefault(cell['politician__faction'], {})[cell['vote']] = cell['vote__count']

    # print(objects)
    list_header = {'vote': 'Vote'}
    return render(request, 'dashboard/genre_votes.html', locals())


def faction_votes(request, name):

    name = unquote(name)
    # TODO: show votes per genre for indiviual factions
    cells = IndividualVoting.objects.filter(voting__date__range=(now() + relativedelta(months=-6), now()),
                                            politician__faction=name).values('voting__genre',
                                                                             'vote').annotate(Count('vote'))
    objects = {}
    for cell in cells:
        objects.setdefault(cell['voting__genre'], {})[cell['vote']] = cell['vote__count']

    return render(request, 'dashboard/faction_votes.html', locals())

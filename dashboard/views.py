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
    start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date = date_form.fields['end_date'].initial
    end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()
    print(start_date, end_date)

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
            print(start_date, end_date)
        else:
            print("data invalid")

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

    last_ten_votings = Voting.objects.all().order_by('-date')[:10]

    return render(request, 'dashboard/index.html', {'number_of_votings': votings_count,
                                                    'genre_labels': genre_labels,
                                                    'genre_counts': genre_counts,
                                                    'faction_votes': faction_votes,
                                                    'total_votes': total_votes,
                                                    'start_date': start_date,
                                                    'end_date': end_date,
                                                    'date_form': date_form,
                                                    'last_ten_votings': last_ten_votings})


def list(request):
    date_form = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date = date_form.fields['start_date'].initial
    start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date = date_form.fields['end_date'].initial
    end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
            print(start_date, end_date)
        else:
            print("data invalid")

    all_votings = Voting.objects.filter(date__range=(start_date, end_date)).order_by('-date')

    return render(request, 'dashboard/list.html', locals())


def detail(request, voting_id):

    specific_voting = Voting.objects.filter(voting_id=voting_id)[0]
    # get politicians related to this specific voting
    pol_objects = Voting.objects.get(voting_id=voting_id).politicians.all().order_by('individualvoting__politician_id')
    # pol_objects.order_by('politician_id')
    # get respective politician's vote - order as previous query!
    pol_votes = IndividualVoting.objects.filter(voting_id=voting_id).order_by('politician_id').values_list('vote',
                                                                                                           flat=True)
    politicians = tuple(zip(pol_objects, pol_votes))

    factions = IndividualVoting.objects.filter(voting_id=voting_id).values_list('politician__faction',
                                                                                flat=True).distinct()

    vote_options = IndividualVoting.objects.values_list('vote', flat=True).distinct()
    vote_options = [vote for vote in vote_options]
    # TODO: keep order of vote_options, however get the list dynamically
    vote_options = ['Ja', 'Nein', 'Enthalten', 'Nicht abgegeben']
    vote_labels = [key for key in specific_voting.votes.keys()]
    votes = [int(n) for n in specific_voting.votes.values()]
    specific_voting = Voting.objects.filter(voting_id=voting_id)[0]

    cells = IndividualVoting.objects.filter(voting_id=voting_id).values('politician__faction',
                                                                        'vote').annotate(Count('vote'))

    objects = {}
    for cell in cells:
        objects.setdefault(cell['politician__faction'], {})[cell['vote']] = cell['vote__count']

    faction_labels = [key for key in objects.keys()]

    faction_votes_count = [[0 for _ in faction_labels] for _ in vote_options]
    for idx, faction in enumerate(faction_labels):
        for vote in vote_options:
            if objects.get(faction).get(vote):
                # print(f"set {faction}'s vote '{vote}' to {objects[faction][vote]}")
                faction_votes_count[vote_options.index(vote)][idx] = objects[faction][vote]

    # print(faction_votes_count)

    return render(request, 'dashboard/detail.html', {'all_factions': factions,
                                                     'politicians': politicians,
                                                     "specific_voting": specific_voting,
                                                     "votes": votes,
                                                     "vote_labels": vote_labels,
                                                     "faction_votes_count": faction_votes_count,
                                                     "faction_labels": faction_labels})


@require_http_methods(["GET", "POST"])
def genre_votes(request, name):

    date_form = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date = date_form.fields['start_date'].initial
    start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date = date_form.fields['end_date'].initial
    end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
            print(start_date, end_date)
        else:
            print("data invalid")

    votings = Voting.objects.filter(date__range=(start_date, end_date), genre=name)

    cells = IndividualVoting.objects.filter(voting__date__range=(start_date, end_date),
                                            voting__genre=name).values('politician__faction',
                                                                       'vote').annotate(Count('vote'))
    # print(cells)
    objects = {}
    for cell in cells:
        objects.setdefault(cell['politician__faction'], {})[cell['vote']] = cell['vote__count']

    # print(objects)
    list_header = {'vote': 'Vote'}
    return render(request, 'dashboard/genre_votes.html', locals())


@require_http_methods(["GET", "POST"])
def faction_votes(request, name):

    date_form = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date = date_form.fields['start_date'].initial
    start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date = date_form.fields['end_date'].initial
    end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
            print(start_date, end_date)
        else:
            print("data invalid")

    name = unquote(name)
    # TODO: show votes per genre for indiviual factions
    cells = IndividualVoting.objects.filter(voting__date__range=(start_date, end_date),
                                            politician__faction=name).values('voting__genre',
                                                                             'vote').annotate(Count('vote'))
    objects = {}
    for cell in cells:
        objects.setdefault(cell['voting__genre'], {})[cell['vote']] = cell['vote__count']

    return render(request, 'dashboard/faction_votes.html', locals())


@require_http_methods(['GET', 'POST'])
def politician(request, politician_id):
    date_form = DateForm()

    # datetime format must be'%d-%m-%Y'
    start_date = date_form.fields['start_date'].initial
    start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').date()
    end_date = date_form.fields['end_date'].initial
    end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').date()

    if request.method == "POST":
        date_form = DateForm(request.POST)
        if date_form.is_valid():
            start_date = date_form.cleaned_data['start_date']
            end_date = date_form.cleaned_data['end_date']
            print(start_date, end_date)
        else:
            print("data invalid")

    politician_query = Politician.objects.filter(id=politician_id)
    politician = politician_query[0] if len(politician_query) != 0 else None
    if politician is None:
        response = f"Ein Politiker mit der ID {politician_id} konnte nicht gefunden werden."
        return render(request, 'dashboard/error.html', {'error': response})

    last_voting = Voting.objects.filter(politicians__id=politician_id).order_by('-date').values('date')
    if len(last_voting) > 0:
        last_voting = last_voting[0]

    votings = Voting.objects.filter(politicians__id=politician_id, date__range=(start_date, end_date)).order_by('-date')

    individual_votes = IndividualVoting.objects.filter(politician__id=politician_id,
                                                       voting_id__in=votings.values_list('voting_id',
                                                                                         flat=True)).values_list('vote',
                                                                                                                 flat=True)

    voting_count = votings.count()
    vote_stats = IndividualVoting.objects.filter(politician__id=politician_id,
                                                 voting__date__range=(start_date,
                                                                      end_date)).values('voting__genre',
                                                                                        'vote').annotate(Count('vote'))

    objects = {}
    for cell in vote_stats:
        objects.setdefault(cell['voting__genre'], {})[cell['vote']] = cell['vote__count']


    genre_counts_yes = [options.get('Ja') if options.get('Ja') else 0 for options in objects.values()]
    genre_counts_no = [options.get('Nein') if options.get('Nein') else 0 for options in objects.values()]
    genre_counts_not_turned_in = [options.get('Nicht abgegeben') if options.get('Nicht abgegeben') else 0 for options in objects.values()]
    genre_counts_enthalten = [options.get('Enthalten') if options.get('Enthalten') else 0 for options in objects.values()]
    genre_options_count = [genre_counts_yes, genre_counts_no, genre_counts_not_turned_in, genre_counts_enthalten]

    genre_counts = [value for value in objects.values()]

    genre_labels = [key for key in objects.keys()]

    return render(request, 'dashboard/politician.html', locals())

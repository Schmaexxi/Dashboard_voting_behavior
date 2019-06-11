from dashboard.models import IndividualVoting


def global_context(request):
    vote_options = IndividualVoting.objects.values_list('vote', flat=True).distinct()
    return locals()

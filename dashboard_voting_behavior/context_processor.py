from dashboard.models import IndividualVoting
from dashboard.forms import DateForm


def global_context(request):
    date_form = DateForm()
    vote_options = IndividualVoting.objects.values_list('vote', flat=True).distinct()
    return locals()

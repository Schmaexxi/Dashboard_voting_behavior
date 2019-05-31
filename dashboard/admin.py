from django.contrib import admin

from .models import Voting, IndividualVoting, Politician


class VotingAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'topic', 'genre', 'date')


class PoliticianAdmin(admin.ModelAdmin):
    list_display = ('pre_name', 'name', 'faction')


admin.site.register(IndividualVoting)
admin.site.register(Voting, VotingAdmin)
admin.site.register(Politician, PoliticianAdmin)

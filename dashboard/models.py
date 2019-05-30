from django.db import models
from django.contrib.postgres.fields import JSONField


class Voting(models.Model):
    voting_id = models.IntegerField(primary_key=True, unique=True)
    date = models.DateField()
    genre = models.CharField(max_length=30)
    topic = models.TextField(default="")
    description = models.TextField()
    votes = JSONField(null=True, blank=True)


class IndividualVoting(models.Model):
    voting_id = models.IntegerField()
    individual_voting = models.ForeignKey(Voting, on_delete=models.CASCADE, null=True)
    politicians = models.ManyToManyField('Politician')
    vote = models.IntegerField(null=True)


class Politician(models.Model):
    name = models.CharField(max_length=30)
    pre_name = models.CharField(max_length=30)
    faction = models.CharField(max_length=60)

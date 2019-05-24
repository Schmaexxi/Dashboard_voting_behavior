from django.db import models
from django.contrib.postgres.fields import JSONField


class Votings(models.Model):
    voting_id = models.AutoField(primary_key=True)
    json = JSONField(null=True, blank=True)

    def __repr__(self):
        return self.json.__repr__()


class Individual_votings(models.Model):
    id = models.AutoField(primary_key=True)
    voting_id = models.IntegerField(unique=True)
    voting = JSONField(null=True, blank=True)

    def __repr__(self):
        return self.voting.__repr__()

"""
class Politician(models.Model):
    name = models.CharField(max_length=200)
    pre_name = models.CharField(max_length=200)
    birth_date = models.DateTimeField('date published')

    def __str__(self):
        return self.pre_name + " " + self.name


class Voting(models.Model):
    votes = models.ForeignKey(Politician, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
"""
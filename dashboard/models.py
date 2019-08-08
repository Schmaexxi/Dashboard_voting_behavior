from django.db import models
from django.contrib.postgres.fields import JSONField


class Voting(models.Model):
    voting_id = models.IntegerField(primary_key=True, unique=True)
    date = models.DateField()
    genre = models.CharField(max_length=30)
    topic = models.TextField(default="")
    description = models.TextField()
    votes = JSONField(null=True, blank=True)


class Politician(models.Model):
    name = models.CharField(max_length=30)
    pre_name = models.CharField(max_length=30)
    faction = models.CharField(max_length=60)
    voting = models.ManyToManyField(Voting,
                                    through='IndividualVoting',
                                    related_name="politicians")

    def __repr__(self):
        return f"{self.pre_name} {self.name } ({self.faction})"

    def __unicode__(self):
        return f"{self.pre_name} {self.name} ({self.faction})"


class IndividualVoting(models.Model):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    vote = models.CharField(max_length=80)

    class Meta:
        # combined primary key
        unique_together = (("politician", "voting",))

from json import JSONEncoder, dumps

# TODO: date as date type


class Vote:
    def __init__(self):
        pass

    def __str__(self):
        return self.genre + "\nAbstimmung vom " + self.date +\
               "\n" + self.top+ "\n" + self.description

    def dict_repr(self):
        return {
                "voting_id": self.id,
                "genre": self.genre,
                "topic": self.topic,
                "date": self.date,
                "description": self.description,
                "votes": self.votes
                }

    id = ""
    votes = {}
    date = ""
    genre = ""
    topic = ""
    description = ""


class Faction:
    def __init__(self):
        pass

    politicians = {}


class Politician:

    pre_name = None
    name = None
    vote = None

    def __init__(self, pre_name, name, vote):
        assert isinstance(pre_name, str)
        assert isinstance(name, str)
        assert isinstance(vote, str)
        self.pre_name = pre_name
        self.name = name
        self.vote = vote


class CustomEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

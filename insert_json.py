import psycopg2, json
from django.db import DatabaseError

conn = psycopg2.connect(dbname="votings", user="dashboard_voting_behavior", password="password")
try:

    with open('/Users/maximilianlangknecht/PycharmProjects/Scrape_votings/votings/votings.json') as file:
        data = json.load(file)

    cur = conn.cursor()

    votings = data['votings']

    counter = 0
    seperator = ""
    for voting in votings:
        if counter == 0 or counter == len(votings)-1:
            seperator = ""
        else:
            seperator = ","
        #print(json.dumps(voting))
        query_string = """INSERT INTO votings.public.dashboard_votings (json) VALUES ('{0}'){1}""".format(json.dumps(voting), seperator)
        print(query_string)
        cur.execute(query_string)
        conn.commit()

except DatabaseError:
    if conn:
        conn.rollback()

finally:
    if conn:
       conn.close()
import psycopg2
import json
import os
from django.db import DatabaseError


def insert_votings(conn, database_table):
    try:

        counter = 0
        try:
            with open(f"./scrape_votings/votings/votings.json") as file:
                data = json.load(file)

            cur = conn.cursor()

            cur.execute(f"SELECT voting_id FROM {database_table}")
            ids = cur.fetchall()

            for voting in data['votings']:
                new_voting = True
                id_ = voting['id']
                for i in ids:
                    if id_ in i:
                        new_voting = False
                if new_voting:
                    print(new_voting, "ID: ", id_)
                    query_string = f"INSERT INTO {database_table} (voting_id, json) VALUES ({id_}, '{json.dumps(voting)}')"

                    cur.execute(query_string)
                    conn.commit()
                    counter += 1

        except DatabaseError:
            if conn:
                conn.rollback()

        print(f"inserted {counter} new votings")
    except DatabaseError:
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


conn = psycopg2.connect(dbname="votings", user="dashboard_voting_behavior", password="password")

db = "votings.public.dashboard_votings"

insert_votings(conn, db)

"""
import psycopg2
import json
import os
from django.db import DatabaseError

# json-field
def insert_votings(conn, database_table):
    try:

        counter = 0

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


# relational scheme
def insert_relatinoal_votings(conn, database_table):
    curs = conn.cursor()
    curs.execute(f"Select * FROM {database_table}")
    colnames = [desc[0] for desc in curs.description]
    colnames = sorted(colnames)

    counter = 0

    with open(f"./scrape_votings/votings/votings.json") as file:
        data = json.load(file)

    cur = conn.cursor()

    cur.execute(f"SELECT voting_id FROM {database_table}")
    ids = cur.fetchall()

    for voting in data['votings']:
        new_voting = True
        id_ = voting['voting_id']
        for i in ids:
            if int(id_) in i:
                new_voting = False
        if new_voting:
            # sort values to be in order with column names
            keys = sorted(voting.keys())
            result = []
            # set json null values to empty strings
            for key in keys:
                if key == 'votes':
                    result.append(json.dumps(voting[key]))
                elif key == 'date':
                    date = voting[key][-4:] + "-" + voting[key][3:5] + "-" + voting[key][:2]
                    result.append(date)
                else:
                    result.append(voting[key] if voting[key] is not None else "")

            print("New voting - ID: ", id_)
            print(result)
            result_str = ','.join("'{0}'".format(x) for x in result)
            print(result_str)
            query_string = f"INSERT INTO {database_table} ({', '.join(colnames)}) VALUES ({result_str})"
            print(query_string)
            cur.execute(query_string)
            conn.commit()
            counter += 1
        else:
            print(" Voting with ID: ", id_, " already exists. Continue.")


    print(f"inserted {counter} new votings")


if __name__ == '__main__':

    conn = psycopg2.connect(dbname="votings", user="dashboard_voting_behavior", password="password")

    db = "votings.public.dashboard_voting"

    #insert_votings(conn, db)
    insert_relatinoal_votings(conn, db)
"""
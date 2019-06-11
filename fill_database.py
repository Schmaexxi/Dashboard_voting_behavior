import psycopg2
import json
import os
from django.db import DatabaseError

# ToDo: regex for the terrible inconsistencies
vote_types = ['Ja', 'Nein','Enthalten', 'Nicht abg.', 'Nicht abg.(Gesetzlicher Mutterschutz)']
# lowercase items as temporary fix
vote_types = [item.lower() for item in vote_types]
# vote_types.index(politician.get('vote').lower()) if politician.get('vote').lower() in vote_types else 4


# TODO: only insert from where you left off
# relational scheme
def insert_relational_votings(conn, database_table):
    curs = conn.cursor()
    curs.execute(f"Select * FROM {database_table}")
    colnames = [desc[0] for desc in curs.description]
    colnames = sorted(colnames)

    counter = 0

    with open(f"./scrape_votings/votings/votings.json", encoding='utf-8') as file:
        data = json.load(file)

    try:
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
    except DatabaseError:
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def insert_politicians_and_votings(conn, database_table_politicians,
                                   db_individual_voting):

    curs = conn.cursor()
    curs.execute(f"Select * FROM {database_table_politicians}")
    colnames_politicians = [desc[0] for desc in curs.description]
    print(colnames_politicians)
    query_set = curs.fetchall()

    for filename in os.listdir("./scrape_votings/votings/individual"):
        with open(f"./scrape_votings/votings/individual/{filename}", encoding='utf-8') as file:
            data = json.load(file)

        # get voting id from filename
        current_voting_id = filename[:filename.rfind(f".")]

        # query existing politicians
        curs.execute(f"Select * FROM {database_table_politicians}")
        query_set = curs.fetchall()

        for faction, politicians in data.items():
            for politician in politicians:
                new_politician = True
                politician_id = 0
                for item in query_set:
                    # check if politician does already exist
                    if new_politician:
                        if politician['name'] == item[colnames_politicians.index('name')] and \
                                politician['pre_name'] == item[colnames_politicians.index('pre_name')] \
                                and faction == item[colnames_politicians.index('faction')]:
                            print("Politician already exists: ", item)
                            politician_id = item[colnames_politicians.index('id')]
                            new_politician = False
                if new_politician:

                    # Insert new politician
                    print("New politician ", politician)
                    query_string = f"INSERT INTO {database_table_politicians} (name, pre_name, faction) VALUES " \
                        f"('{politician.get('name')}','{politician.get('pre_name')}', '{faction}') RETURNING id"
                    # print(query_string)
                    curs.execute(query_string)
                    politician_id = curs.fetchall()[0][0]
                    # print(politician_id)
                    conn.commit()

                # TODO: fix inconsistencies - see if statement in query string
                # Insert new relation between pilitician and individual voting
                query_string = f"INSERT INTO {db_individual_voting} (voting_id, politician_id, vote) " \
                    f"VALUES ('{current_voting_id}', '{politician_id}', '{politician.get('vote')}')"
                # print(query_string)
                curs.execute(query_string)
                conn.commit()


if __name__ == '__main__':

    conn = psycopg2.connect(dbname="votings", user="dashboard_voting_behavior", password="password")

    db_voting = "votings.public.dashboard_voting"
    db_politician = "votings.public.dashboard_politician"
    db_individual_voting = "votings.public.dashboard_individualvoting"

    insert_relational_votings(conn, db_voting)
    if conn.closed:
        conn = psycopg2.connect(dbname="votings", user="dashboard_voting_behavior", password="password")
    insert_politicians_and_votings(conn, db_politician, db_individual_voting)

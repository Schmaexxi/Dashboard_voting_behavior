from typing import List, Dict, Union, Tuple, Optional
import psycopg2
import json
import os
from django.db import DatabaseError


def insert_relational_votings(conn, database_table: str) -> Union[List[int], None]:
    """
    function for inserting voting data from a json file into a database table
    :param conn: psycopg2 connection
    :param database_table: name of table for 'votings'
    :return: list of votings that had already been in the table
    """
    curs = conn.cursor()
    curs.execute(f"Select * FROM {database_table}")
    colnames: List[str] = [desc[0] for desc in curs.description]
    colnames = sorted(colnames)
    counter: int = 0

    # json file with the data to be inserted
    with open(f"./scrape_votings/votings/votings.json", encoding='utf-8') as file:
        data: Dict[str, List[Union[Dict[str, Union[str, int]], int]]] = json.load(file)

    ids: None = None

    try:
        cur = conn.cursor()

        # get ids of existent votings
        cur.execute(f"SELECT voting_id FROM {database_table}")
        ids: List[Tuple[int]] = cur.fetchall()
        ids: List[int] = [x[0] for x in ids]

        for voting in data['votings']:
            new_voting: bool = True
            id_: int = voting['voting_id']
            if int(id_) in ids:
                new_voting = False
            if new_voting:
                # sort values to be in order with column names
                keys: List[str] = sorted(voting.keys())
                result: List[str] = []
                # set json null values to empty strings
                for key in keys:
                    if key == 'votes':
                        result.append(json.dumps(voting[key]))
                    elif key == 'date':
                        date: str = voting[key][-4:] + "-" + voting[key][3:5] + "-" + voting[key][:2]
                        result.append(date)
                    else:
                        result.append(voting[key] if voting[key] is not None else "")

                # print("New voting - ID: ", id_, result)
                result_str: str = ','.join("'{0}'".format(x) for x in result)
                # print(result_str)
                query_string: str = f"INSERT INTO {database_table} ({', '.join(colnames)}) VALUES ({result_str})"
                # print(query_string)
                cur.execute(query_string)
                conn.commit()
                counter += 1
            else:
                pass
                # print(" Voting with ID: ", id_, " already exists. Continue.")

        print(f"inserted {counter} new votings")
    except DatabaseError:
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
    return ids


def insert_politicians_and_votings(conn, database_table_politicians: str,
                                   db_individual_voting: str, existent_votings=[]):
    """
    function to insert politicians and their votes from json files into database tables
    :param conn: psycopg2 connection
    :param database_table_politicians: name of table for 'politicians'
    :param db_individual_voting: name of table for 'individual_votings'
    :param existent_votings: list of already existing votings
    :return: None
    """

    curs = conn.cursor()
    curs.execute(f"Select * FROM {database_table_politicians}")
    colnames_politicians: List[str] = [desc[0] for desc in curs.description]
    # print(colnames_politicians)
    query_set = curs.fetchall()

    dir_: str = "./scrape_votings/votings/individual"
    num_votings: int = len([name for name in os.listdir(dir_) if os.path.isfile(os.path.join(dir_, name))])

    for num, filename in enumerate(os.listdir(dir_)):
        id_: str = filename[:filename.find('.')]
        if int(id_) in existent_votings:
            # print("voting already exists. skipping")
            continue
        # print(f"Progress: {num/num_votings*100} %")
        with open(f"{dir_}/{filename}", encoding='utf-8') as file:
            data: Dict[str, List[Union[Dict[str, Union[str, int]], int]]] = json.load(file)

        # get voting id from filename
        current_voting_id: str = filename[:filename.rfind(f".")]

        # query existing politicians
        curs.execute(f"Select * FROM {database_table_politicians}")
        query_set: List[Tuple[Optional, ]] = curs.fetchall()

        for faction, politicians in data.items():
            for politician in politicians:
                new_politician: bool = True
                politician_id: int = 0
                for item in query_set:
                    # check if politician does already exist
                    if new_politician:
                        if politician['name'] == item[colnames_politicians.index('name')] and \
                                politician['pre_name'] == item[colnames_politicians.index('pre_name')] \
                                and faction == item[colnames_politicians.index('faction')]:
                            # print("Politician already exists: ", item)
                            politician_id = item[colnames_politicians.index('id')]
                            new_politician = False
                if new_politician:

                    # Insert new politician
                    # print("New politician ", politician)
                    query_string = f"INSERT INTO {database_table_politicians} (name, pre_name, faction) VALUES " \
                        f"('{politician.get('name')}','{politician.get('pre_name')}', '{faction}') RETURNING id"
                    # print(query_string)
                    curs.execute(query_string)
                    politician_id = curs.fetchall()[0][0]
                    # print(politician_id)
                    conn.commit()

                # Insert new relation between pilitician and individual voting
                query_string: str = f"INSERT INTO {db_individual_voting} (voting_id, politician_id, vote) " \
                    f"VALUES ('{current_voting_id}', '{politician_id}', '{'Nicht abgegeben' if politician.get('vote').lower().startswith('nicht abg') else politician.get('vote')}')"
                # print(query_string)
                try:
                    curs.execute(query_string)
                    conn.commit()
                except Exception as e:
                    # violates unique constraint
                    if e.pgcode == "25P02":
                        print(e)
                    conn.rollback()


if __name__ == '__main__':
    os.environ.setdefault('PGDATABASE', 'votings')
    os.environ.setdefault('PGUSER', 'dashboard_voting_behavior')
    os.environ.setdefault('PGPASSWORD', 'password')

    conn = psycopg2.connect("")
    db_voting: str = "dashboard_voting"
    db_politician: str = "dashboard_politician"
    db_individual_voting: str = "dashboard_individualvoting"

    existent_votings = insert_relational_votings(conn, db_voting)

    if conn.closed:
        conn = psycopg2.connect("")
    insert_politicians_and_votings(conn, db_politician, db_individual_voting, existent_votings=existent_votings)

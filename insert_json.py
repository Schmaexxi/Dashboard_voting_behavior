import psycopg2, json
from django.db import DatabaseError
import os

# TODO: use wrapper to ensure database connection and exceptin handling
# query jsonfield from database
# if json_keys is None query all rows
# json_keys dict of rowname-json_key pairs
def get_column(cursor, database, json_keys=None, constraint=None):
    """

    :param cursor:
    :param database:
    :param json_keys:
    :param constraint:
    :return:
    """
    tables = "*"
    if not json_keys is None:
        tables = "".join(["""{0}->'{1}',""".format(key, value) for key, value in json_keys.items()])
        tables = tables[:-1]
    query_string = """SELECT {0} FROM {1}""".format(tables, database)
    if constraint:
        query_string += """ WHERE {}""".format(constraint)
    cursor.execute(query_string)
    return cursor.fetchall()


def insert_json(conn, database_table, column_name, path_to_json_file):
    """Insert json into specific column

    :param conn: psycopg2 connection
    :param database_table: str - full specification of database table
    :param column_name: str - column name
    :param path_to_json_file: str
    :return: None
    """
    try:
        with open(path_to_json_file) as file:
            data = json.load(file)
        #print(json.dumps(data, indent=4))
        cur = conn.cursor()

        votings = data['votings']

        record_set = get_column(cur, database_table, json_keys={'json': 'id'})
        id_list = [x[0] for x in record_set]


        new_voting = None

        for idx, voting in enumerate(votings):
            if voting['id'] in id_list:
                continue
            else:
                new_voting = True
                print("New id: {}".format((voting['id'])))
            query_string = f"INSERT INTO {database_table} ({column_name}) VALUES ('{json.dumps(voting)}')"
            print(query_string)
            cur.execute(query_string)
            conn.commit()

        if new_voting is None:
            print("No new votings")

    except DatabaseError:
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()


def insert_json_array(conn, database_table, column_name):
    try:
        list_of_ods = []
        counter = 0
        for filename in os.listdir("./scrape_votings/votings/individual"):
            new_voting = True
            try:
                with open(f"./scrape_votings/votings/individual/{filename}") as file:
                    data = json.load(file)

                id_ = filename[:filename.rfind(f".")]
                cur = conn.cursor()

                cur.execute(f"SELECT voting_id FROM {database_table}")
                ids = cur.fetchall()
                id_ = int(id_)
                list_of_ods.append(id_)

                for i in ids:
                    if id_ in i:
                        new_voting = False

                if new_voting:
                    print(new_voting, "ID: ", id_)
                    query_string = f"INSERT INTO {database_table} (voting_id, voting) VALUES ({id_}, '{json.dumps(data)}')"
                    # print(query_string)

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


if __name__ == '__main__':

    # TODO: specify relative path
    path = '/Users/maximilianlangknecht/PycharmProjects/Scrape_votings/votings/votings.json'
    conn = psycopg2.connect(dbname="votings", user="dashboard_voting_behavior", password="password")

    db = "votings.public.dashboard_votings"
    column = 'json'
    
    cur = conn.cursor()

    #insert_json(conn, db, column, path)

    insert_json_array(conn, "votings.public.dashboard_individual_votings",
                      "voting")


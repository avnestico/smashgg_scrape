import os
from urllib import parse

import psycopg2 as psycopg2
from psycopg2.extensions import AsIs


def db_connect():
    """
    Write tournament data to postgres database
    Requires env variable DATABASE_URL of the form: postgres://<username>:<password>@<IP address>:<port>/<db name>
    :return conn, cur: database connection and cursor
    """
    try:
        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor()
    except:
        print("I am unable to connect to the database.")
        conn = None
        cur = None

    return conn, cur


def db_create(cur):
    """
    Create game database
    :param cur: database cursor
    :return:
    """
    games = ["melee", "wii_u", "smash_64"]
    commands = {"tournaments":  # %s = <game>_tournaments
        """
        CREATE TABLE IF NOT EXISTS "%s" (
            slug VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            score INT,
            attendees JSONB
        )
        """,
        "players":  # %s = <game>_players
        """
        CREATE TABLE IF NOT EXISTS "%s" (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            tournaments JSONB
        )
        """,
        "leaders":  # %s = <game>_leaders
        """
        CREATE TABLE IF NOT EXISTS "%s" (
            game VARCHAR(15) NOT NULL,
            date DATE,
            leaders JSONB
        )
        """
    }

    for key in commands:
        for game in games:
            table_name = game + "_" + key
            try:
                cur.execute(commands[key] % table_name)
                print("Successfully created table " + table_name)
            except:
                print("could not create table " + table_name)


def db_check(cur):
    """
    Check databases
    :param cur: database cursor
    :return: None
    """

    try:
        cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        print(cur.fetchall())
    except:
        print("I can't SELECT * FROM pg_catalog.pg_tables")


def db_write_player(cur, game, id, name):
    """
    Write tournament data to postgres database
    :param cur: database cursor
    :param game: game name
    :param tournament: tournament to write
    :return: None
    """

    table_name = to_under(game) + "_players"
    try:
        query = """INSERT INTO "%s" (id, name) VALUES (%%s, %%s)""" % table_name
        cur.execute(query, (id, name))
        print(cur.fetchall())
    except:
        print("I can't INSERT %s into table %s_players" % name, game)


def to_under(game):
    """
    Replace dashes with underscores
    :param game:
    :return game:
    """
    return game.replace("-", "_")

import os
from urllib import parse

import psycopg2 as psycopg2
from psycopg2.extensions import AsIs


def db_connect():
    """
    Write tournament data to postgres database
    :return cur: database cursor
    """
    try:
        parse.uses_netloc.append("postgres")
        url = parse.urlparse(os.environ["DATABASE_URL"])
        print(url)

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
        cur = None

    return cur


def db_create(cur):
    """
    Create game database
    :param cur: database cursor
    :return:
    """
    commands = (
        """
        CREATE TABLE IF NOT EXISTS melee_tournaments (
            slug VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            score INT,
            attendees JSONB
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS melee_players (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            tournaments JSONB
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS wii_u_tournaments (
            LIKE melee_tournaments
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS wii_u_players (
            LIKE melee_players
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS smash_64_tournaments (
            LIKE melee_tournaments
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS smash_64_players (
            LIKE melee_players
        )
        """
    )

    for command in commands:
        try:
            cur.execute(command)
            print("Successfully executed" + command)
        except:
            print("could not execute" + command)


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


def db_write(cur, game, tournament):
    """
    Write tournament data to postgres database
    :param cur: database cursor
    :param game: game name
    :param tournament: tournament to write
    :return: None
    """

    try:
        cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        print(cur.fetchall())
    except:
        print("I can't SELECT * FROM pg_catalog.pg_tables")
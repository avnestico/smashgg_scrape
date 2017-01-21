import json
import math
from datetime import datetime
from random import randint

import psycopg2 as psycopg2
import pytz as pytz
import requests


def dump_tournament(tournament, event):
    """
    Dump all of a tournament's placements
    :param tournament: Smashgg tournament slug
    :param event: game name
    :return: dict containing tournament info
    """
    ## Get tournament name and date
    tournament_url = "https://api.smash.gg/tournament/" + tournament
    t = requests.get(tournament_url)
    tournament_data = t.json()
    print(tournament_data)
    tournament_name = tournament_data["entities"]["tournament"]["name"]
    timezone = tournament_data["entities"]["tournament"]["timezone"]

    # Scrape event page in case event ends earlier than tournament
    event_url = "https://api.smash.gg/tournament/" + tournament + "/event/" + event + "-singles"
    e = requests.get(event_url)
    event_data = e.json()
    id = event_data["entities"]["event"]["id"]
    print("ID:", id)

    timestamp = event_data["entities"]["event"]["endAt"]
    if not timestamp:
        timestamp = tournament_data["entities"]["tournament"]["endAt"]

    # Get local date
    date = datetime.fromtimestamp(timestamp, pytz.timezone(timezone)).date()

    ## Get standings
    standing_url = event_url + "/standings"
    s = requests.get(standing_url)
    s_data = s.json()
    count = s_data["total_count"]
    print("Total entrants:", count)

    # API limits requests to 100 at a time, so we need to request multiple pages
    pages = math.ceil(count/100)

    attendees = {}

    while len(attendees) < count:
        before = len(attendees)
        for i in range(pages):
            page = i + 1
            # Attendees API scrape is inconsistent so we need to add a random string to the end of the url
            # so we can fetch the same page multiple times if necessary
            player_url = "https://api.smash.gg/tournament/" + tournament + "/attendees?per_page=100&filter={\"eventIds\":" +\
                         str(id) + "}&page=" + str(page) + "&a=" + str(randint(0,999))
            print(player_url)
            p = requests.get(player_url)
            p_data = p.json()
            players = p_data["items"]["entities"]["attendee"]

            # Find each player's placement in the given game
            for player in range(len(players)):
                player_id = players[player]["playerId"]
                name = players[player]["player"]["gamerTag"]
                entered_events = players[player]["entrants"]
                for event in range(len(entered_events)):
                    if entered_events[event]["eventId"] == id:
                        attendees[player_id] = {"name": name, "place": entered_events[event]["finalPlacement"]}

        # If whole loop finds no new attendees, assume that they cannot be found from attendees page
        after = len(attendees)
        print("Entrants found:", after)
        if after == before:
            break

    tournament_dict = {tournament: {"name": tournament_name, "date": str(date), "attendees": attendees}}
    return tournament_dict


def json_open(game):
    """
    Open a game's json text file
    :param game: name of game
    :return: dict of json data
    """
    with open(game + ".txt", "a+") as existing:
        existing.seek(0)
        try:
            tournaments = json.load(existing)
        except json.decoder.JSONDecodeError:
            tournaments = {}
    return tournaments


def json_write(game, tournament_list, force=False):
    """
    Write tournament(s) to json text file
    :param game: name of game
    :param tournament_list: list of slugs to scrape
    :param force: set True to overwrite existing data
    :return: None
    """
    tournaments = json_open(game)

    for tournament in tournament_list:
        if force or tournament not in tournaments.keys():
            dump = dump_tournament(tournament, game)
            for key in dump.keys():
                tournaments[key] = dump[key]

    with open(game + ".txt", "w") as file:
        json.dump(tournaments, file)


def print_date(dict, tournament_list=None):
    """
    Print tournament names and dates
    :param dict: dict of tournament
    :param tournament_list: subset of tournaments to check. If None, print all.
    :return: None
    """
    if not tournament_list:
        tournament_list = dict.keys()
    for tournament in tournament_list:
        name = dict[tournament]["name"]
        date = dict[tournament]["date"]
        print(name, date, sep=": ")


def db_write(game, tournament):
    """
    Write tournament data to postgres database
    :param game: game name
    :param tournament: tournament to write
    :return: None
    """
    try:
        conn = psycopg2.connect("dbname=postgres user=postgres password=postgres")
    except:
        print("I am unable to connect to the database.")


if __name__ == "__main__":
    melee_events = ["olympus",
                    "apollo",
                    "shots-fired-2"]
    json_write("melee", melee_events)
    print_date(json_open("melee"))
    """
    db_write("melee", None)"""

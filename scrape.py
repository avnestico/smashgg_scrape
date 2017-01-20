import json
import math
from datetime import datetime
from random import randint

import psycopg2 as psycopg2
import pytz as pytz
import requests


def dump_tournament(tournament, event):
    tournament_url = "https://api.smash.gg/tournament/" + tournament
    t = requests.get(tournament_url)
    tournament_data = t.json()
    print(tournament_data)
    timezone = tournament_data["entities"]["tournament"]["timezone"]

    event_url = "https://api.smash.gg/tournament/" + tournament + "/event/" + event + "-singles"
    e = requests.get(event_url)
    event_data = e.json()
    id = event_data["entities"]["event"]["id"]
    print("ID:", id)

    epoch = event_data["entities"]["event"]["endAt"]
    if not epoch:
        epoch = tournament_data["entities"]["tournament"]["endAt"]

    standing_url = event_url + "/standings"
    s = requests.get(standing_url)
    s_data = s.json()
    count = s_data["total_count"]
    print("Total entrants:", count)

    pages = math.ceil(count/100)

    attendees = {}

    while len(attendees) < count:
        before = len(attendees)
        for i in range(pages):
            page = i + 1
            player_url = "https://api.smash.gg/tournament/" + tournament + "/attendees?per_page=100&filter={\"eventIds\":" + str(id) + "}&page=" + str(page) + "&a=" + str(randint(0,999))
            print(player_url)
            p = requests.get(player_url)
            p_data = p.json()
            players = p_data["items"]["entities"]["attendee"]
            for player in range(len(players)):
                player_id = players[player]["playerId"]
                name = players[player]["player"]["gamerTag"]
                entered_events = players[player]["entrants"]
                for event in range(len(entered_events)):
                    if entered_events[event]["eventId"] == id:
                        attendees[player_id] = {"name": name, "place": entered_events[event]["finalPlacement"]}

        after = len(attendees)
        print("Entrants found:", after)
        if after == before:
            break

    tournament_dict = {tournament: {"date": epoch, "timezone": timezone, "attendees": attendees}}

    return tournament_dict


def json_open(game):
    with open(game + ".txt", "a+") as existing:
        existing.seek(0)
        try:
            tournaments = json.load(existing)
        except json.decoder.JSONDecodeError:
            tournaments = {}
    return tournaments


def json_write(game, tournament_list, force=False):
    tournaments = json_open(game)

    for tournament in tournament_list:
        if force or tournament not in tournaments.keys():
            dump = dump_tournament(tournament, game)
            for key in dump.keys():
                tournaments[key] = dump[key]

    with open(game + ".txt", "w") as file:
        json.dump(tournaments, file)


def print_date(json, tournament_list=None):
    if not tournament_list:
        tournament_list = json.keys()
    for tournament in tournament_list:
        epoch = json[tournament]["date"]
        timezone = json[tournament]["timezone"]

        tz = pytz.timezone(timezone)
        dt = datetime.fromtimestamp(epoch, tz)
        print(dt.strftime('%Y-%m-%d'))


def db_write(game, tournament):
    try:
        conn = psycopg2.connect("dbname=postgres user=postgres password=postgres")
    except:
        print("I am unable to connect to the database.")


if __name__ == "__main__":
    """melee_events = ["olympus",
                    "apollo",
                    "shots-fired-2"]
    json_write("melee", melee_events)
    print_date(json_open("melee"))"""
    db_write("melee", None)

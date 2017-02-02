import json
import math
from datetime import datetime

import pytz as pytz
import requests

import database as db


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
    tournament_name = tournament_data["entities"]["tournament"]["name"]
    timezone = tournament_data["entities"]["tournament"]["timezone"]

    # Scrape event page in case event ends earlier than tournament
    event_url = "https://api.smash.gg/tournament/" + tournament + "/event/" + event + "-singles"
    e = requests.get(event_url)
    event_data = e.json()
    event_id = event_data["entities"]["event"]["id"]

    timestamp = event_data["entities"]["event"]["endAt"]
    if not timestamp:
        timestamp = tournament_data["entities"]["tournament"]["endAt"]

    # Get local date
    date = datetime.fromtimestamp(timestamp, pytz.timezone(timezone)).date()

    ## Get standings
    standing_string = "/standings?expand[]=attendee&per_page=100"
    standing_url = event_url + standing_string
    s = requests.get(standing_url)
    s_data = s.json()
    count = s_data["total_count"]
    print("Total entrants:", count)

    # API limits requests to 100 at a time, so we need to request multiple pages
    pages = math.ceil(count/100)

    attendees = {}

    while len(attendees) < count:
        for i in range(pages):
            page = i + 1
            if page != 1:
                standing_url = event_url + standing_string + "&page=" + str(page)
                s = requests.get(standing_url)
                s_data = s.json()

            players = s_data["items"]["entities"]["attendee"]

            # Find each player's placement in the given game
            for player in range(len(players)):
                player_id = players[player]["playerId"]
                name = players[player]["player"]["gamerTag"]
                entered_events = players[player]["entrants"]
                for event in range(len(entered_events)):
                    if entered_events[event]["eventId"] == event_id:
                        attendees[int(player_id)] = {int(entered_events[event]["finalPlacement"])}
                # db.db_write_player

    tournament_dict = {tournament: {"name": tournament_name, "date": str(date), "attendees": attendees}}  # points
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


if __name__ == "__main__":
    """melee_events = ["olympus",
                    "apollo",
                    "shots-fired-2",
                    "genesis-3"]
    json_write("melee", melee_events)
    print_date(json_open("melee"))
    """
    conn, cur = db.db_connect()
    db.db_create(cur)
    db.db_check(cur)
    #conn.commit()
    cur.close()
    conn.close()

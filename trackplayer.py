import os
import requests
from bs4 import BeautifulSoup
import re
import psycopg2
from dotenv import load_dotenv
from messager import Texter

load_dotenv()

db_host = os.environ.get('HOST')
db_database = os.environ.get('DATABASE')
db_user = os.environ.get('USER')
db_password = os.environ.get('PASSWORD')
conn = psycopg2.connect(
    host=db_host,
    database=db_database,
    user=db_user,
    password=db_password
)

pujols_query = """
    SELECT hitting, hr FROM player_status WHERE name = 'a. pujols';
"""
cur = conn.cursor()
cur.execute(pujols_query)
pujols_status, pujols_hrs = cur.fetchone()
print(f"PUJOLS HITTING STATUS: {pujols_status}")


def update_player(name, field, new_val):
    cur.execute(
        f"""
        UPDATE player_status
        SET {field} = {new_val}
        WHERE name = '{name}';
        """
    )
    conn.commit()

phone_numbers_query = """
            SELECT phone_number FROM users;
        """
cur.execute(phone_numbers_query)
phone_numbers = cur.fetchall()
texter = Texter()

base_url = "https://www.espn.com/mlb/scoreboard"
print(f"Requesting page from {base_url}")
page_raw = requests.get(base_url)
print("Converting to soup object.")
page = BeautifulSoup(page_raw.content, 'html.parser')
print("Finding scoreboards.")
scoreboards = page.find_all('section', class_='Scoreboard')
print("Finding teamnames.")
game_id = 0
for scoreboard in scoreboards:
    team_names = scoreboard.find_all('div', class_='ScoreCell__TeamName')
    for team_name in team_names:
        if team_name.text == 'Cardinals':
            sb_str = str(scoreboard)
            game_id = re.search(r' id="([0-9])+">', sb_str).group()[5:-2]
            # need to check for if game has started and isn't over
            print(f'Bingo. {game_id}')
            break
    else:
        continue
    break
if game_id == 0:
    print("Cards don't play today.")
else:
    game_url = f"https://www.espn.com/mlb/game/_/gameId/{game_id}"
    print(f"game_url = {game_url}")
    game_page_raw = requests.get(game_url)
    game_page = BeautifulSoup(game_page_raw.content, 'html.parser')
    player = game_page.find('h3', class_='gameStatus__playerIntro__playerName')
    player_name = ""
    if player:
        player_name = player.text
    else:
        players = game_page.find_all('section', class_='gameStatus__batterPitcher__athlete')
        if len(players) == 0:
            print("Player not batting")
            exit(0)
        lisname = players[1].text.split()
        player_name = " ".join([lisname[0][-2:], lisname[1]])
    player_name = player_name.lower()
    if not pujols_status:
        if player_name == "a. pujols":
            # send text
            message = f"""
            Albert Pujols is currently batting. He is {700-pujols_hrs} dingers away
            from 700.
            """
            for number in phone_numbers:
                texter.send_text(message, number[0])
            update_player(player_name, 'hitting', True)

    else:
        if player_name != "a. pujols":
            # find ab result
            ab_url = game_url.replace("game", "playbyplay", 1)
            ab_raw = requests.get(ab_url)
            ab_page = BeautifulSoup(ab_raw.content, 'html.parser')
            result = ab_page.find('li', id=lambda x: x and x.startswith(f'allPlays{game_id}')).text.split(".")[0]
            print(result)
            homerun = False
            if "Pujols homered" in result.text:
                homerun = True
            if homerun:
                # send text
                for number in phone_numbers:
                    texter.send_text(f"""
                    Albert Pujols has hit homerun #{pujols_hrs+1}
                    """)
                update_player(player_name, 'hr', pujols_hrs+1)
            update_player(player_name, 'hitting', False)
            pass

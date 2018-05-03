import predict
import psycopg2
import pandas as pd
import numpy as np


nbrOfFeatures = 3

def ranking(wantedTempo, wantedLoudness, wantedMode, user):
    cursor = connect_database()
    dict = get_songdata(cursor)
    ranking = {}

    # Vi går igenom vår lista och sätter vikter på alla låtar
    for index, row in dict.iterrows():
        ranking[row['songid']] = weight(row, wantedTempo, wantedLoudness, wantedMode, cursor, user)

    # Sedan sorterar vi rankingen efter vikterna
    return sort_dict_by_weight(ranking)

# Funktion som räknar ut vikten på en låt baserat på hur väl den stämmer med vad tensorflow tycker
# vi ska spela
# Vi ska inkludera userbias här också för individuella låtar.
def weight(dictRow, wantedTempo, wantedLoudness, wantedMode, cursor, user):
    songssinceMultiplier = 1
    modeWeight = 0
    tempoWeight = 0
    loudnessWeight = -0.01 * abs(wantedLoudness-dictRow.loudness) ** 2 + 1
    if(wantedMode == dictRow.mode):
        modeWeight = 1
    if(abs(wantedTempo-dictRow.tempo)<=10):
        tempoWeight = -0.01 * (wantedTempo-dictRow.tempo) ** 2 + 1
    bias = get_userbias(user, dictRow.songid, cursor)
    if(get_songssinceplayed(user, dictRow.songid, cursor) < 20)
        songssinceMultiplier = 0  # Bör bytas ut mot någon funktion som beror mer på antalet låtar sedan spelning
    weight = (loudnessWeight + modeWeight + tempoWeight + bias)/(nbrOfFeatures + 1) * songssinceMultiplier
    return weight

# Funktion som sorterar en dictionary vars keys är songids och values är weights och
# returnerar en lista på de 10 songids som har högst weight
def sort_dict_by_weight(dict):
    try:
        tracklist = sorted(dict, key=dict.__getitem__, reverse=True)[:10]
    except Exception as e:
        print("Unable to sort. Make sure input is a valid dictionary")
        print(e)
    return tracklist

def get_songdata(cursor):
    try:
        cursor.execute("SELECT songid, tempo, mode, loudness FROM songdata")
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    df = pd.DataFrame(columns=['songid', 'tempo', 'mode', 'loudness'])
    count = 0
    for record in cursor:
        df.loc[count] = [record[0], record[1], record[2], record[3]]
        count += 1
    return df

def connect_database():
    # Här hämtar vi datan från postgresSQL
    # Och ordnar den i ett korrekt format
    try:
        conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='databasen'")
    except Exception as e:
        print("I am unable to connect to the database")
        print(e)
    cursor = conn.cursor()
    return cursor

def get_userbias(user, songid, cursor):
    try:
        cursor.execute("""SELECT rating FROM userdata_userdata WHERE userid=%s AND songid=%s;""", (user,songid))
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    arr = []
    for record in cursor:
        arr.append(record[0])
    count = 1
    avg = 0
    total = 0
    for a in arr:
        total = total + a
        avg = total/count
        count = count + 1
    return avg

#Funktion som returnerar hur många låtar sedan en låt spelades för användaren senast
def get_songssinceplayed(user, songid, cursor):
    try:
        cursor.execute("SELECT SongCounter.lastPlayed, UserPlayCounter.playCounter FROM SongCounter INNER JOINS "
                       "UserPlayCounter ON SongCounter.userid=UserPlayCounter.userid"
                       "WHERE SongCounter.userid=%s AND SongCounter.songid=%s;", (user, songid))
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    counterdata = cursor.fetchone()
    lastplayed, playcounter = counterdata
    result = playcounter - lastplayed
    return result
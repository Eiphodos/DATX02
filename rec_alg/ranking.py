# Note: FULKOD (EJ FUNGERANDE)
# Temporärt ranking algoritm som kanske ersätts av någonting annat senare

import predict
import psycopg2
import pandas as pd
import numpy as np

nbrOfFeatures = 3

def ranking(wantedTempo, wantedLoudness, wantedMode, user):
    # Vilka övriga inputs får vi från predict?
    #switch beroende på hur vi implementerar chunksen?
    # (tempo, genre, mode, releaseyear)


    # PROBLEM OCH FRÅGETECKEN
    # Hur hanterar vi "konstiga" kombinationer där vi inte får tillbaka något som ger riktiga låtar
    # Sortera istället för filtrera?
    # Random ranking av en filtrerad lista?
    # Kan sätta arbiträra vikter vid alla inputs och ranka efter hur många och hur väl dom stämmer

    # Dictionary med all statisk data för låtarna vi använder oss av
    # Kommer snarare läsas från en databas
    cursor = connect_database()
    dict = get_songdata(cursor)
    #dict.set_index('songid', inplace=True)
    # Temporär dictionary som används för rankingen
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
    loudnessWeight = 0
    modeWeight = 0
    tempoWeight = 0
    loudnessWeight = -0.01 * abs(wantedLoudness-dictRow.loudness) ** 2 + 1
    if(wantedMode == dictRow.mode):
        modeWeight = 1
    if(abs(wantedTempo-dictRow.tempo)<=10):
        tempoWeight = -0.01 * (wantedTempo-dictRow.tempo) ** 2 + 1
    bias = get_userbias(user, dictRow.songid, cursor)
    weight = (loudnessWeight + modeWeight + tempoWeight + bias)/(nbrOfFeatures + 1)
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
        cursor.execute("SELECT rating FROM userdata_userdata")
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
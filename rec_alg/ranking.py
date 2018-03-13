# Note: FULKOD (EJ FUNGERANDE)
# Temporärt ranking algoritm som kanske ersätts av någonting annat senare

import predict

def ranking():
    # Vilka övriga inputs får vi från predict?
    (tempo, genre, mode, releaseyear) = predict.predict()

    # PROBLEM OCH FRÅGETECKEN
    # Hur hanterar vi "konstiga" kombinationer där vi inte får tillbaka något som ger riktiga låtar
    # Sortera istället för filtrera?
    # Random ranking av en filtrerad lista?
    # Kan sätta arbiträra vikter vid alla inputs och ranka efter hur många och hur väl dom stämmer

    # Dictionary med all statisk data för låtarna vi använder oss av
    # Kommer snarare läsas från en databas
    dict = get_songdata()
    # Temporär dictionary som används för rankingen
    ranking = {songid, weight}


    # Vi går igenom vår lista och sätter vikter på alla låtar
    for d in dict:
        ranking.append(d.songid, weight(d))

    # Sedan sorterar vi rankingen efter vikterna
    sort(ranking, weight)

# Funktion som räknar ut vikten på en låt baserat på hur väl den stämmer med vad tensorflow tycker
# vi ska spela
def weight(dict):
    weight = (dict.genre == genre) + (dict.mode == mode)
    return weight

def get_songdata():
    # Här hämtar vi datan från postgresSQL
    # Och ordnar den i ett korrekt format
    return data
import sys
sys.path.append("/home/musik/DATX02/tensor-v2/")
import CBandit
sys.path.append("/home/musik/DATX02/server/userdata/")
import Bucketizer

import psycopg2

# Bandit checkpoint paths
LOUD_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/cbandit/loud"
TEMPO_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/cbandit/tempo"
MODE_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/cbandit/mode"
# Bandits constant variables
CB_NUMBER_OF_STATES = 28
CB_TEMPO_ACTIONS = 10
CB_MODE_ACTIONS = 2
CB_LOUD_ACTIONS = 7
CB_TIME_BUCKETS = 4


# Skapar en anslutning till databsen
def connect_database():
    try:
        conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='databasen'")
    except Exception as e:
        print("I am unable to connect to the database")
        print(e)
    return conn

# Returnerar en array med all data som cbandit ej tränats på som har ett ratingid (alltså data som
# direkt hör ihop med actions som cbandit har föreslagit).
def get_untrained_rids(cursor):
    try:
        cursor.execute("""SELECT rating, ratingid FROM userdata_userdata WHERE cbtrained=false AND ratingid IS NOT NULL;""")
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    arr = []
    count = 0
    for record in cursor:
        arr[count] = (record[0],record[1])
        count += 1
    return arr

# Returnerar en array med data som cbandit ej har tränats men som inte har ett ratingid kopplat till sig. Alltså data
# Som andra neurala nätverk har samlat in.
# Vi räknar sedan baklänges för att se vilka actions en cbandit hade gjort för att föreslå dom låtarna.
def get_untrained_actstates(cursor):
    try:
        cursor.execute("""SELECT rating, userid, heartrate, time, songid FROM userdata_userdata WHERE cbtrained=false AND ratingid IS NULL;""")
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    tempoarr = []
    modearr = []
    loudarr = []
    count = 0
    conn = connect_database()
    cursor2 = conn.cursor()
    for record in cursor:
        state = calculate_state(record[1], record[2], record[3], cursor2)
        reward = record[0]
        tmp, md, ld = calculate_actions(cursor2, record[4])
        tempoarr[count] = (reward, state, tmp)
        modearr[count] = (reward, state, md)
        loudarr[count] = (reward, state, ld)
        count += 1
    conn.close()
    return tempoarr, modearr, loudarr

def calculate_state(userid, heartrate, time, cursor):
    try:
        cursor.execute("""SELECT userindex FROM userdata_userplaycounter WHERE userid=%s;""", (userid,))
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    usernumber = 0
    for record in cursor:
        usernumber = record[0]
    bucketedpulse = Bucketizer.bucketize_pulse(heartrate)
    bucketedtime = Bucketizer.bucketize_time(time)
    return usernumber*CB_NUMBER_OF_STATES + bucketedpulse*CB_TIME_BUCKETS + bucketedtime

def calculate_actions(cursor, songid):
    try:
        cursor.execute("""SELECT tempo, mode, loudness FROM songdata WHERE songid=%s;""", (songid,))
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    tempo = 0
    mode = 0
    loud = 0
    for record in cursor:
        tempo = Bucketizer.rev_bucket_tempo(record[0])
        mode = record[1]
        loud = Bucketizer.rev_bucket_loud(record[2])
    return tempo, mode, loud

def cleanup(cursor):
    try:
        cursor.execute("UPDATE userdata_userdata SET cbtrained='true' WHERE cbtrained='false'")
    except Exception as e:
        print("Something went wrong when trying to UPDATE")
        print(e)


def main():
    # Bandits
    loudbandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_LOUD_ACTIONS, LOUD_CKPT_PATH)
    modebandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_MODE_ACTIONS, MODE_CKPT_PATH)
    tempobandit = CBandit.CBandit(CB_NUMBER_OF_STATES, CB_TEMPO_ACTIONS, TEMPO_CKPT_PATH)

    conn = connect_database()
    cursor = conn.cursor()
    rrlist = get_untrained_rids(cursor)
    tempolist, modelist, loudlist = get_untrained_actstates(cursor)

    tempobandit.train_all(rrlist, tempolist)
    modebandit.train_all(rrlist, modelist)
    loudbandit.train_all(rrlist, loudlist)

    cleanup(cursor)
    conn.close()

# If we run module as a script, run main
if __name__ == '__main__':
    main()
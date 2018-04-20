import sys
sys.path.append("/home/musik/DATX02/tensor-v2/")
import DNNModel
sys.path.append("/home/musik/DATX02/server/userdata/")
import Bucketizer

import psycopg2
import pandas as pd

# DNN checkpoint paths
DNN_LOUD_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/loud"
DNN_TEMPO_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/tempo"
DNN_MODE_CKPT_PATH = "/home/musik/DATX02/tensor-v2/checkpoints/dnn/mode"


# Skapar en anslutning till databsen
def connect_database():
    try:
        conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='databasen'")
    except Exception as e:
        print("I am unable to connect to the database")
        print(e)
    return conn


def get_training_data(cursor):
    try:
        cursor.execute("""SELECT rating, userid, heartrate, time, songid FROM userdata_userdata;""")
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    traindict = {'userid', 'heartrate', 'time', 'rating'}
    userarr = []
    hrarr = []
    timearr = []
    ratingarr = []
    tempoarr = []
    modearr = []
    loudarr = []
    conn = connect_database()
    cursor2 = conn.cursor()
    for record in cursor:
        ratingarr.append(record[0])
        userarr.append(record[1])
        hrarr.append(record[2])
        timearr.append(record[3])
        tmp, md, ld = get_songdata(cursor2, record[4])
        tempoarr.append(tmp)
        modearr.append(md)
        loudarr.append(ld)
    traindict['user_id'] = userarr
    traindict['heart_rate'] = hrarr
    traindict['rating'] = ratingarr
    traindict['time'] = timearr
    conn.close()
    return traindict, tempoarr, modearr, loudarr

def get_songdata(cursor, songid):
    try:
        cursor.execute("""SELECT tempo, mode, loudness FROM songdata WHERE songid=%s;""", (songid,))
    except Exception as e:
        print("Something went wrong when trying to SELECT")
        print(e)
    tempo = 0
    mode = 0
    loud = 0
    for record in cursor:
        tempo = record[0]
        mode = record[1]
        loud = record[2]
    return tempo, mode, loud

def main():
    # DNN output types
    dnn_outputloud = Bucketizer.BucketType.LOUDNESS
    dnn_outputmode = Bucketizer.BucketType.MODE
    dnn_outputtempo = Bucketizer.BucketType.TEMPO

    # DNN estimators
    LoudDNN = DNNModel.DNNModel(DNN_LOUD_CKPT_PATH, dnn_outputloud)
    ModeDNN = DNNModel.DNNModel(DNN_MODE_CKPT_PATH, dnn_outputmode)
    TempoDNN = DNNModel.DNNModel(DNN_TEMPO_CKPT_PATH, dnn_outputtempo)

    conn = connect_database()
    cursor = conn.cursor()
    trainfeatures, tempolabels, modelabels, loudlabels = get_training_data(cursor)

    LoudDNN.train(features=trainfeatures, labels=loudlabels)
    ModeDNN.train(features=trainfeatures, labels=modelabels)
    TempoDNN.train(features=trainfeatures, labels=tempolabels)
    conn.close()

# If we run module as a script, run main
if __name__ == '__main__':
    main()
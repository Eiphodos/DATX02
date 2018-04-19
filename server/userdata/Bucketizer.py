from enum import Enum

def bucketize_pulse(heartrate):
    buckets = [40, 60, 80, 100, 120, 150, 180]
    index = 0
    for b in buckets:
        if (heartrate < b):
            return index
        index += 1
    return index

def bucketize_time(timeval):
    if (timeval > 300 and timeval < 660):
        return 0
    if (timeval > 659 and timeval < 960):
        return 1
    if (timeval > 959 and timeval < 1320):
        return 2
    if (timeval > 1319 or timeval < 300):
        return 3

def bucketize_tempo(tempoindex):
    buckets = [30, 50, 70, 90, 110, 130, 150, 170, 190, 210]
    return buckets[tempoindex]

def bucketize_loudness(loudindex):
    buckets = [-8, -6, -4, -2, 0, 2, 5]
    return buckets[loudindex]

def getLabelsBucket(labels, type):
    result = []
    if (type == BucketType.PULSE):
        for l in labels:
            result.append(bucketize_pulse(l))
    if (type == BucketType.TIME):
        for l in labels:
            result.append(bucketize_time(l))
    if (type == BucketType.TEMPO):
        for l in labels:
            result.append(bucketize_tempo(l))
    if (type == BucketType.LOUDNESS):
        for l in labels:
            result.append(bucketize_loudness(l))

    return result

def getNumberOfClassesForType(type):
    if (type == BucketType.PULSE):
        return 8
    if (type == BucketType.TIME):
        return 4
    if (type == BucketType.TEMPO):
        return 10
    if (type == BucketType.LOUDNESS):
        return 7
    return 0

def getNameForType(type):
    if (type == BucketType.PULSE):
        return "bpm"
    if (type == BucketType.TIME):
        return "time"
    if (type == BucketType.TEMPO):
        return "tempo"
    if (type == BucketType.LOUDNESS):
        return "loudness"
    return ""

class BucketType(Enum):
    PULSE = 0
    TIME = 1
    TEMPO = 2
    LOUDNESS = 3
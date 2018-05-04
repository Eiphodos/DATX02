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
    buckets = [-30, -25, -20, -15, -10, -5, 0]
    return buckets[loudindex]

def bucketize_mode(mode):
    return mode


# Tempo buckets #
# 0-30 = index 0
# 31-50 = index 1
# 51-70 = index 2
# 71-90 = index 3
# 91-110 = index 4
# 111-130 = index 5
# 131-150 = index 6
# 151-170 = index 7
# 171-190 = index 8
# 191-inf  = index 9
def rev_bucket_tempo(tempo):
    buckets = [30, 50, 70, 90, 110, 130, 150, 170, 190, 210]
    count = 0
    for b in buckets:
        if (count >= 8):
            if (tempo >= b):
                count += 1
            else:
                return count
    return count

def rev_bucket_loud(loud):
    buckets = [-30, -25, -20, -15, -10, -5, 0]
    count = 0
    for b in buckets:
        if (loud <= b):
            return count
        count += 1
    return count

def getLabelsBucket(labels, type):
    result = []
    if (type == BucketType.MODE):
        for l in labels:
            result.append(bucketize_mode(l))
    if (type == BucketType.TIME):
        for l in labels:
            result.append(bucketize_time(l))
    if (type == BucketType.TEMPO):
        for l in labels:
            result.append(rev_bucket_tempo(l))
    if (type == BucketType.LOUDNESS):
        for l in labels:
            result.append(rev_bucket_loud(l))

    return result

def getNumberOfClassesForType(type):
    if (type == BucketType.MODE):
        return 2
    if (type == BucketType.TIME):
        return 4
    if (type == BucketType.TEMPO):
        return 10
    if (type == BucketType.LOUDNESS):
        return 7
    return 0

def getNameForType(type):
    if (type == BucketType.MODE):
        return "mode"
    if (type == BucketType.TIME):
        return "time"
    if (type == BucketType.TEMPO):
        return "tempo"
    if (type == BucketType.LOUDNESS):
        return "loudness"
    return ""

class BucketType(Enum):
    MODE = 0
    TIME = 1
    TEMPO = 2
    LOUDNESS = 3
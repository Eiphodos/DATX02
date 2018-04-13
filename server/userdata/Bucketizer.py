class Bucketizer:
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
        buckets = [-20, -15, -10, -5, 0, 5, 10, 15, 20]
        return buckets[loudindex]

import librosa

def get_beat_times(test):
    y, sr = librosa.load("audio/linedance.mp3")
    onset_env = librosa.onset.onset_strength(y, sr=sr)
    dynamic_tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)
    return dynamic_tempo
    
def beat():
    y, sr = librosa.load("audio/linedance.mp3")
    tempo, beats = librosa.beat.beat_track(y, sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    

"""
    Approximation of the timestamp of beats calculated using the bpm of that moment
"""
def beatTimestamps(filename):
    # get dynamic tempo as frames
    y, sr = librosa.load("audio/linedance.mp3")
    onset_env = librosa.onset.onset_strength(y, sr=sr)
    dynamic_tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)

    # get amount of dynamic tempo frames per second
    step = len(dynamic_tempo)/librosa.get_duration(y=y, sr=sr)

    # TODO: Make function
    # Get beats detected by Librosa for comparison and correcting
    tempo, beats = librosa.beat.beat_track(y, sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)

    index = 0
    i = 0
    timestamp = 0
    correctings = 0
    dynamic_beat_timestamps = []
    while True:
        # break if no more frames available
        if i > len(dynamic_tempo):
            break
        index += 1

        # seconds per beat
        spb = 1/(dynamic_tempo[int(i)]/60)
        timestamp += spb
        dev = spb/2

        # correct timestamp if $beat_times's timestamp falls within range of current timestamp
        if index < len(beat_times) and timestamp - dev <= beat_times[index] <= timestamp + dev:
            timestamp = beat_times[index]
            correctings += 1
        
        # append timestamp
        dynamic_beat_timestamps.append(timestamp)
        i += (step*spb)

    print('timestamp correctings: ', correctings)
    return dynamic_beat_timestamps
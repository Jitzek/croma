import librosa

def calculate_bpm():
    y, sr = librosa.load("audio/linedance.mp3")
    onset_env = librosa.onset.onset_strength(y, sr=sr)
    dynamic_tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)
    print(dynamic_tempo)
    
def beat():
    y, sr = librosa.load("audio/linedance.mp3")
    tempo, beats = librosa.beat.beat_track(y, sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    
    
    
def get_beat_times(filename):
    y, sr = librosa.load(filename)
    tempo, beats = librosa.beat.plp(y, sr)
    return librosa.frames_to_time(beats, sr=sr)
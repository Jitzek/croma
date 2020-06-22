import librosa


class AudioAnalysing:
    def __init__(self, filename):
        self.filename = filename
        self.y, self.sr = librosa.load(self.filename)

    def get_dynamic_tempo(self):
        onset_env = librosa.onset.onset_strength(self.y, sr=self.sr)
        dynamic_tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.sr, aggregate=None)
        return dynamic_tempo
    
    def get_beat_times(self):
        tempo, beats = librosa.beat.beat_track(self.y, self.sr)
        return librosa.frames_to_time(beats, sr=self.sr)

    """
        Approximation of the timestamps of beats calculated using the bpm of that moment

        returns:
            array : dynamic_beat_timestamps, array containing all detected timestamps of a beat
    """
    def get_dynamic_beat_times(self):
        # get dynamic tempo as frames
        onset_env = librosa.onset.onset_strength(self.y, sr=self.sr)
        dynamic_tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.sr, aggregate=None)

        # get amount of dynamic tempo frames per second
        step = len(dynamic_tempo)/librosa.get_duration(y=self.y, sr=self.sr)

        # Get beats detected by Librosa for comparison and correcting
        beat_times = self.get_beat_times()

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

        print('Timestamp Corrections:', correctings)
        return dynamic_beat_timestamps
# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
import statistics
import operator
from models import ArtistModel, VenueModel, PerformanceModel, TrackModel
import urllib.parse
from collections import Counter

import json
import re

class ArtistService:
    def __init__(self):
        self.model = ArtistModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_performances(self, artist_name):
        # escape single-quote
        artist_name = artist_name.replace("'", r"\'")
        return self.model.get_all_performances(artist_name)

    def get_mb_tags(self, artist_name):
        # escape single-quote
        artist_name = artist_name.replace("'", r"\'")
        return self.model.get_mb_tags(artist_name)


class VenueService:
    def __init__(self):
        self.model = VenueModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_count(self):
        return self.model.get_all_count()

    def get_location(self,venue_name):
        venue_name = venue_name.replace("'", r"\'")
        return self.model.get_location(venue_name)

class PerformanceService:
    def __init__(self):
        self.model = PerformanceModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_tracks(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_all_tracks(perf_name)

    def get_venue(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_venue(perf_name)

    def get_artist(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_artist(perf_name)

    def get_date(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_date(perf_name)

    def get_description(self, perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_description(perf_name)

class TrackService:
    def __init__(self):
        self.model = TrackModel()

    def get_all(self):
        return self.model.get_all()

    def get_count(self):
        return self.model.get_all_count()

    def get_artists(self, track_name):
        # escape single-quote
        track_name = track_name.replace("'", r"\'")
        track_name = track_name.replace("#", r"\#")
        return self.model.get_artist(track_name)

    def get_performances(self, track_name):
        # escape single-quote
        track_name = track_name.replace("'", r"\'")
        track_name = track_name.replace("#", r"\#")
        return self.model.get_performances(track_name)

    def get_analyses(self,artist,track_name):
        tracks = self.model.get_analyses(artist,track_name)
        track_tempos = []

        # keep track of the predicted keys
        predicted_keys = []
        # for each performances track
        for track, track_info in tracks.items():

            #unpack tempos from tracks
            track_tempos.append(int(track_info[2]))

            # add the key with the majority percentage in this performances
            predicted_keys.append(max(track_info[0].items(), key=operator.itemgetter(1))[0])


        avg_tempo = statistics.mean(track_tempos)
        max_tempo = max(track_tempos)


        key_counter = Counter(predicted_keys)
        key_percentages = [(key, key_counter[key] / len(predicted_keys) * 100.0) for key in key_counter]

        return tracks,track_tempos,avg_tempo,max_tempo,predicted_keys,key_percentages, track_info[3]

    #right now only returns the guster details
    def get_actual_tempo_and_key(self):
        return self.model.get_actual_tempo_and_key()
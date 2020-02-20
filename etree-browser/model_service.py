# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
import statistics
import operator
from models import ArtistModel, VenueModel, PerformanceModel, TrackModel
import urllib.parse
from collections import Counter
import numpy as np
import json
import re
import k_med
import copy
from sklearn_extra.cluster import KMedoids
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

    def get_venue(self,venue_name):
        venue_name = venue_name.replace("'", r"\'")
        return self.model.get_venue(venue_name)

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
        #WARNING: this value should be removed
        return self.model.get_all(1)

    def get_performance(self,perf_name):
        perf_name = perf_name.replace("'", r"\'")
        return self.model.get_performance(perf_name)

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
            track_tempos.append(track_info[2])

            # add the key with the majority percentage in this performances
            predicted_keys.append(max(track_info[0].items(), key=operator.itemgetter(1))[0])


        avg_tempo = statistics.mean(track_tempos)
        max_tempo = max(track_tempos)


        key_counter = Counter(predicted_keys)
        key_percentages = [(key, key_counter[key] / len(predicted_keys) * 100.0) for key in key_counter]

        #The arrays we'll be using for medoids
        track_tempos_arr = np.asarray(track_tempos)
        track_lengths = track_info[3]
        predicted_keys = [x.strip(' ') for x in predicted_keys]
        enumerated_keys = copy.deepcopy(predicted_keys)
        key_set = enumerate(set(enumerated_keys))
       # enumerated_keys = enumerate(enumerated_keys)

        #this will be replaced by
        #for item in enumerated_keys:
            #print(item)

        for key in range(0,len(enumerated_keys)):
            for enum, name in enumerate(set(predicted_keys),start=1):
                #print("enum:" + str(name))
                if enumerated_keys[key] == name:
                    #print(str(enumerated_keys[key])+" " + str(name))
                    enumerated_keys[key] = enum

        #print(enumerated_keys)
        k_tracks = np.array([track_tempos_arr , track_lengths, enumerated_keys]).transpose()
        k_tracks = np.around(k_tracks,4)

        #Scikits k medoids algorithm
        k_medoids = KMedoids(n_clusters=5, random_state=0).fit_predict(k_tracks)
        print(k_medoids)
        #print(k_tracks)
        #print(k_tracks.shape)
        #MEDIODS TEST: parms are number of feature types and k clustrs
        #medoids_initial = self.init_medoids(k_tracks, 3)
        #print("inital medoids:" + str(medoids_initial))

        #S = self.compute_d_p(k_tracks, medoids_initial, 2)
        #print('\n'.join([''.join(['{:4} '.format(item) for item in row])
                        # for row in S]))

        #labels = self.assign_labels(S)
        #print(labels)
        k=4
        p=2
        medoids_and_labels = k_med.kmedoids(k_tracks,k,p,starting_medoids = None,max_steps = np.inf)
        #my own k_medoids algorithm labels
        labels = medoids_and_labels[1]
        print(medoids_and_labels)
        return tracks,track_tempos,avg_tempo,max_tempo,predicted_keys,key_percentages, track_info[3], k_medoids

    #right now only returns the guster details
    def get_actual_tempo_and_key(self):
        return self.model.get_actual_tempo_and_key()

    def get_calma_track(self, artist_name, track_name):
        # escape single-quote
        #track_name = track_name.replace("'", r"\'")
        #track_name = track_name.replace("#", r"\#")
        return self.model.get_calma_track(artist_name,track_name)
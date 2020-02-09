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

        k_tracks = np.array([track_tempos_arr , track_lengths]).transpose()
        k_tracks = np.around(k_tracks,4)
        print(k_tracks)
        print(k_tracks.shape)
        #MEDIODS TEST: parms are number of feature types and k clustrs
        #medoids_initial = self.init_medoids(k_tracks, 3)
        #print("inital medoids:" + str(medoids_initial))

        #S = self.compute_d_p(k_tracks, medoids_initial, 2)
        #print('\n'.join([''.join(['{:4} '.format(item) for item in row])
                        # for row in S]))

        #labels = self.assign_labels(S)
        #print(labels)
        k=3
        p=2
        medoids_and_labels = self.kmedoids(k_tracks,k,p,starting_medoids = None,max_steps = np.inf)
        labels = medoids_and_labels[1]
        print(medoids_and_labels)
        return tracks,track_tempos,avg_tempo,max_tempo,predicted_keys,key_percentages, track_info[3], labels

    #right now only returns the guster details
    def get_actual_tempo_and_key(self):
        return self.model.get_actual_tempo_and_key()
    #1.initialization phase
    def init_medoids(self,X, k):
        from numpy.random import choice, seed
        seed(1)
        #Generate a uniform random sample from the range of indexes
        #with length k without replacement (can't pick same index twice)
        samples = choice(len(X), size=k, replace=False)
        #a matrix of the sampled medoids
        return X[samples, :]

    #2.Computing the distance matrix
    # no of columns is the number of medoids or clusters()
    # no of rows is the number of data points
    def compute_d_p(self,X,medoids,p):
        m = len(X)
        medoids_shape = medoids.shape
        #if 1-d array provided, reshape to single 2d array
        if len(medoids_shape) == 1:
            medoids = medoids.reshape((1,len(medoids)))
        k = len(medoids)

        S = np.empty((m,k))

        for i in range(m):
            d_i = np.linalg.norm(X[i,:]-medoids, ord = p, axis = 1)
            S[i,:] = np.around(d_i**p,4)
        return S

    #3.Cluster assignment: check for each data point which medoid is closer to it
    #and assign it that label
    def assign_labels(self, S):
        return np.argmin(S,axis = 1)
    #4.Swap test,
    def update_medoids(self,X,medoids,p):
        #recompute distance matrix
        S = self.compute_d_p(X, medoids, p)
        labels = self.assign_labels(S)

        out_medoids = medoids
        #for each cluster
        for i in set(labels):

            avg_dissimilarity = np.sum(self.compute_d_p(X, medoids[i], p))

            cluster_points = X[labels == i]
            #search if any of the points in the cluster decreases the average
            #dissimilarity coefficient
            for datap in cluster_points:
                new_medoid = datap
                new_dissimilarity = np.sum(self.compute_d_p(X, new_medoid, p))

                if new_dissimilarity < avg_dissimilarity:
                    avg_dissimilarity = new_dissimilarity
                    #the point in the cluster which decreases the dissimilarity the most
                    #will be chosen
                    out_medoids[i] = new_medoid

        return out_medoids

    # check whether medoids have changed
    def has_converged(self, old_medoids, medoids):
        return set([tuple(x) for x in old_medoids]) == set([tuple(x) for x in medoids])

        # Full algorithm
    def kmedoids(self, X, k, p, starting_medoids=None, max_steps=np.inf):
        if starting_medoids is None:
            medoids = self.init_medoids(X, k)
        else:
            medoids = starting_medoids

        converged = False
        labels = np.zeros(len(X))
        i = 1
        while (not converged) and (i <= max_steps):
            old_medoids = medoids.copy()

            S = self.compute_d_p(X, medoids, p)

            labels = self.assign_labels(S)

            medoids = self.update_medoids(X, medoids, p)

            converged = self.has_converged(old_medoids, medoids)
            i += 1
        return (medoids, labels)
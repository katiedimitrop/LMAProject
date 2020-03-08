#LINK: global distance funcion http://www.ieee.ma/uaesb/pdf/distances-in-classification.pdf

# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
import pandas as pd
from models import TrackModel
import math
import random
import pandas as pd
import pandas as pd
import numpy as np
import statistics
from matplotlib import pyplot as plt
from pyclustering.utils import distance_metric, type_metric, calculate_distance_matrix
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import scale
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_samples, silhouette_score

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

from pyclustering.cluster.kmedoids import kmedoids

class ClusterService:
    def __init__(self):
        self.model = TrackModel()

    #can use custom distance matrix with this one
    #furthermore it should automatically find outliers
    def get_dbscan_for_track(self, artist_name, track_name):

        # ############################### Data prep #################################
        #hardcoded matrix of distances between keys in circle of fifths
        key_dist = np.zeros(shape=(12, 12))
        for ri, row in enumerate(key_dist):
            for ci, col in enumerate(row):
                dif = abs(ci - ri)
                if dif <= 6:
                    key_dist[ri][ci] = abs(ci - ri)
                else:
                    key_dist[ri][ci] = 12 - abs(ci - ri)

        track_analysis = self.model.get_analysis_for_track(artist_name,track_name)

        features =  track_analysis[['Track duration','Tempo','Max Key']]
        # scale and standardize
        #scale duration,tempo,key
        #X = StandardScaler().fit_transform(features)
        # reduce to two dimensions
        #X = PCA(n_components=2).fit_transform(X)

        #isolate DURATION,TEMPO
        reducable_frame = features[['Track duration','Tempo']]

        ######## TIME AND TEMPO ############
        scaled_cols = StandardScaler().fit_transform(reducable_frame)
        #print(str(scaled_cols))

        #reduce to two dimensions
        reduced_cols =  PCA(n_components=1).fit_transform(scaled_cols)
        reduced_floats = []
        # this isolates the feature(s) describing tempo and duration
        for row in reduced_cols:
            reduced_floats.append(row[0])

        reduced_data = pd.DataFrame({'reduced': reduced_floats})


        #print(str(reduced_cols))

        ############ KEYS ###########
        key_col = []

        keys = track_analysis[['Max Key']].values

        for row in keys:
            #enumerate the minor keys with the same index as their relative major keys (same key signature)
            if row[0] == 24:
                key == math.nan
            elif row[0] == 21:
                key = 0
            elif row[0] == 16:
                key = 1
            elif row[0] == 23:
                key = 2
            elif row[0] == 18:
                key = 3
            elif row[0] == 13:
                key = 4
            elif row[0] == 20:
                key = 5
            elif row[0] == 15:
                key = 6
            elif row[0] == 22:
                key = 7
            elif row[0] == 17:
                key = 8
            elif row[0] == 12:
                key = 9
            elif row[0] == 9:
                key = 10
            elif row[0] == 14:
                key = 11
            else: #major keys
                key = row[0]
            key_col.append(key)

        #not all keys will be in the [0,11] range

        #reorder the keys, C, G, D, A instead of C, C#, D, D#
        keys_mapped = []
        for row in key_col:
            if row % 2 == 0:
                keys_mapped.append(row)
            else:
                keys_mapped.append((row + 6) % 12)

        print(str(keys_mapped))


        scaled_lists  = StandardScaler().fit_transform((np.asarray(keys_mapped)).reshape(-1, 1))
        scaled_keys = []
        for row in scaled_lists:
            scaled_keys.append(row[0])
        #print(str(scaled_keys))


        #print(str(reduced_data))
        print(str(key_dist))
        ##calculate dissimilarities of UNSCALED keys
        feature_keys = np.zeros(shape=(len(keys_mapped), len(keys_mapped)))
        for ri, row in enumerate(feature_keys):
            for ci, col in enumerate(row):
               # print("ROW "+str(ri)+" COLUMN " + str(ci) + str(row))
                #print(str(len(keys_mapped)))
                #print(str(len(key_dist)))
                #print(str(len(feature_keys)))
                #print(max(keys_mapped))
                feature_keys[ri][ci] = key_dist[int(keys_mapped[ri])][int(keys_mapped[ci])]

        # version of reduced data combined with keys
        unused_data = pd.DataFrame({'reduced': reduced_floats, 'key': scaled_keys})

        dissimilarities = 0.8* metrics.pairwise_distances(reduced_data, metric='euclidean') + 0.2* feature_keys
        #dissimilarities = metrics.pairwise_distances(reduced_data, metric='euclidean')

        # ############################# EPSILON value ###############################
        # Epsilon and min samples
        # DMDBSCAN technique to find suitable epsilon for each density level
        # in set

        #calculate the distance of each point to it's nearest neighbour
        neigh = NearestNeighbors(n_neighbors = 2)
        nbrs = neigh.fit(reduced_data)
        #return those distances and their indices
        distances, indices = nbrs.kneighbors(reduced_data)

        #indices is a list of index pairs
        #(an index, it's nearest neigbout)

        #sort and plot results
        distances = np.sort(distances, axis=0)

        #isolate just the values, without axis id
        distances = distances[:,1]
        plt.figure(0)
        plt.title("Graph for finding optimal epsilon value (DBSCAN)")
        plt.xlabel("Number of performances")
        plt.ylabel("Distance of each performance to it's closest neighbour (Sorted)")
        #UNCOMMENTED TEMPORARILY
        plt.plot(distances)
        #point of max curvature will be optimal epsilon
        plt.savefig('epsilon.png', dpi=192)


        ################################## Execute ######################################
        db = DBSCAN(eps=0.5,min_samples=10,metric = 'precomputed').fit(dissimilarities)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        clusters = db.labels_

        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(clusters)) - (1 if -1 in clusters else 0)
        n_noise_ = list(clusters).count(-1)

        #print('Estimated number of clusters: %d' % n_clusters_)
        #print('Estimated number of noise points: %d' % n_noise_)

        ######################### Silhouette (min_samples) ###############################
        #mean silhoette over all samples
        print("Silhouette Coefficient: %0.3f"
              % metrics.silhouette_score(dissimilarities, clusters, metric='precomputed'))
        # ############################ Plot clustering ################################

        plt.figure(1)

        colors = ['royalblue', 'maroon', 'forestgreen', 'mediumorchid', 'tan', 'deeppink', 'olive', 'goldenrod',
                 'lightcyan', 'navy']
        vectorizer = np.vectorize(lambda x: colors[x % len(colors)])
        plt.scatter(reduced_data,scaled_keys, c=vectorizer(clusters))
        plt.savefig('dbscan.png', dpi=192)



        #append labels to output dataset

        outlier_indices = []
        #get outlier indices
        for index,label in enumerate(clusters):
            if label == -1:
                outlier_indices.append(index)


        dissimilarities = np.delete(dissimilarities, outlier_indices,axis = 0)
        dissimilarities = np.delete(dissimilarities, outlier_indices, axis = 1)
        scaled_keys = np.delete(scaled_keys, outlier_indices)
        reduced_floats = np.delete(reduced_floats, outlier_indices, axis=0)
        non_outlier_labels= self.get_kmedoids_for_track( artist_name, track_name,dissimilarities,reduced_floats,scaled_keys)

        #update "clusters" labels based on kmedoids output
        non_ouliers_index= 0
        for index,label in enumerate(clusters):
            if label != -1:
                clusters[index] = non_outlier_labels[non_ouliers_index]
                non_ouliers_index+=1

        track_analysis['Labels'] = pd.Series(clusters, index=track_analysis.index)
        # display the cluster labels and their size
        unique_elements, counts = np.unique(clusters, return_counts=True)
        print(np.asarray((unique_elements, counts)))

        return track_analysis

    def get_kmedoids_for_track(self, artist_name, track_name, diss,reduced_data,scaled_keys):

        ############################ Data prep #####################################

        track_analysis = self.model.get_analysis_for_track(artist_name,track_name)

        features = track_analysis[['Track duration', 'Tempo','Max Key']]
        # scale and standardize
        #X = StandardScaler().fit_transform(features)
        # reduce to two dimensions
        #X = PCA(n_components=2).fit_transform(X)

        #Cluster number will be 3
        initial_medoids = [50,175,200]

        ############################ Execute kmedoids #####################################
        metric = distance_metric(type_metric.EUCLIDEAN)
        kmedoids_instance = kmedoids(diss, initial_medoids, data_type='distance_matrix')
        #kmedoids_instance = kmedoids(X, initial_medoids,metric = metric)
        kmedoids_instance.process()
        clusters = kmedoids_instance.get_clusters()
        medoids = kmedoids_instance.get_medoids()

        #distances = 0.5*np.array(time_tempo_dist) + 0.5*np.array(feature_keys)
        # create K-Medoids algorithm for processing distance matrix instead of points



        #fix the output representation (clusters matrix) into the one required by my
        #app (labels array)
        #store the label of the cluster at the 0th index
        for index,list in enumerate(clusters):
            list[0] = index

        print(medoids)
        labels = np.zeros(len(diss),dtype=int)
        for list in clusters:
            for index_item in list:
                labels[index_item] = list[0]
        ######################### Silhouette (min_samples) ###############################
        X  = pd.DataFrame({'reduced': reduced_data, 'key': scaled_keys})
        # mean silhoette over all samples
        print("Silhouette Coefficient: %0.3f"
        % metrics.silhouette_score(diss, labels, metric = 'precomputed'))

        ############################# Plot clustering ################################

        plt.figure(2)

        colors = ['royalblue', 'maroon', 'forestgreen', 'mediumorchid', 'tan', 'deeppink', 'olive', 'goldenrod',
                  'lightcyan', 'navy']

        vectorizer = np.vectorize(lambda x: colors[x % len(colors)])
        plt.scatter(reduced_data,scaled_keys, c=vectorizer(labels))

        plt.savefig('kmedoids.png', dpi=192)

        # display the cluster labels and their size
        unique_elements, counts = np.unique(clusters, return_counts=True)
        print(np.asarray((unique_elements, counts)))

        #add labels to output features
        #track_analysis['Labels'] = pd.Series(labels, index=track_analysis.index)
        return labels#track_analysis

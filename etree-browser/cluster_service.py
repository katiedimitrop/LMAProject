#LINK: global distance funcion http://www.ieee.ma/uaesb/pdf/distances-in-classification.pdf

# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
import pandas as pd
from models import TrackModel
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


        track_analysis = self.model.get_analysis_for_track(artist_name,track_name)

        features =  track_analysis[['Track duration','Tempo','Max Key']]

        reducable_frame = features[['Track duration','Tempo']]
        print(str(reducable_frame))
        #scale and standardize
        scaled_cols = StandardScaler().fit_transform(reducable_frame)
        print(str(scaled_cols))
        #reduce to two dimensions
        reduced_cols = PCA(n_components=1).fit_transform(scaled_cols)
        print(str(reduced_cols))
        reduced_floats = []
        key_col = []

        keys = track_analysis[['Max Key']].values

        for row in keys:
            #enumerate the minor keys with the same index as their relative major keys (same key signature)
            if row[0] == 21:
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

        #reorder the keys
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
        print(str(scaled_keys))

        for row in reduced_cols:
            reduced_floats.append(row[0])

        reduced_data = pd.DataFrame({'reduced': reduced_floats, 'key' : scaled_keys})


        #Key preprocessing
        print(str(reduced_data))


        dissimilarities = metrics.pairwise_distances(reduced_data, metric='euclidean')

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
              % metrics.silhouette_score(reduced_data, clusters))

        # ############################ Plot clustering ################################

        plt.figure(1)

        colors = ['royalblue', 'maroon', 'forestgreen', 'mediumorchid', 'tan', 'deeppink', 'olive', 'goldenrod',
                 'lightcyan', 'navy']
        vectorizer = np.vectorize(lambda x: colors[x % len(colors)])
        plt.scatter(reduced_data.values[:, 0], reduced_data.values[:, 1], c=vectorizer(clusters))
        plt.savefig('dbscan.png', dpi=192)

        #display the cluster labels and their size
        unique_elements, counts = np.unique(clusters, return_counts=True)
        print(np.asarray((unique_elements, counts)))

        #append labels to output dataset
        track_analysis['Labels'] = pd.Series(clusters, index=track_analysis.index)
        return track_analysis

    def get_kmedoids_for_track(self, artist_name, track_name):
        ############################ Data prep #####################################

        track_analysis = self.model.get_analysis_for_track(artist_name,track_name)

        features = track_analysis[['Track duration', 'Tempo','Max Key']]
        # scale and standardize
        X = StandardScaler().fit_transform(features)
        # reduce to two dimensions
        X = PCA(n_components=2).fit_transform(X)

        #Cluster number will be 3
        initial_medoids = [50,175,300]

        ############################ Execute kmedoids #####################################
        metric = distance_metric(type_metric.EUCLIDEAN)

        kmedoids_instance = kmedoids(X.tolist(), initial_medoids,metric = metric)
        kmedoids_instance.process()
        clusters = kmedoids_instance.get_clusters()
        medoids = kmedoids_instance.get_medoids()

        #distances = 0.5*np.array(time_tempo_dist) + 0.5*np.array(feature_keys)
        # create K-Medoids algorithm for processing distance matrix instead of points
        #kmedoids_instance = kmedoids(distances, initial_medoids, data_type='distance_matrix')


        #fix the output representation (clusters matrix) into the one required by my
        #app (labels array)
        #store the label of the cluster at the 0th index
        for index,list in enumerate(clusters):
            list[0] = index

        print(medoids)
        labels = np.zeros(len(track_analysis),dtype=int)
        for list in enumerate(clusters):
            for index_item in list:
                labels[index_item] = list[0]
        ######################### Silhouette (min_samples) ###############################

        # mean silhoette over all samples
        print("Silhouette Coefficient: %0.3f"
        % metrics.silhouette_score(X, labels))

        ############################# Plot clustering ################################

        plt.figure(2)

        colors = ['royalblue', 'maroon', 'forestgreen', 'mediumorchid', 'tan', 'deeppink', 'olive', 'goldenrod',
                  'lightcyan', 'navy']

        vectorizer = np.vectorize(lambda x: colors[x % len(colors)])
        plt.scatter(X[:, 0], X[:, 1], c=vectorizer(labels))

        plt.savefig('kmedoids.png', dpi=192)

        # display the cluster labels and their size
        unique_elements, counts = np.unique(clusters, return_counts=True)
        print(np.asarray((unique_elements, counts)))

        #add labels to output features
        track_analysis['Labels'] = pd.Series(labels, index=track_analysis.index)
        return track_analysis

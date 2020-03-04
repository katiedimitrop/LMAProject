# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
import pandas as pd
from models import TrackModel
import pandas as pd
import pandas as pd
import numpy as np
import statistics
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import scale
from sklearn_extra.cluster import KMedoids
from sklearn.metrics import silhouette_samples, silhouette_score
class ClusterService:
    def __init__(self):
        self.model = TrackModel()

    def get_analysis_for_track(self, artist_name, track_name):

        track_analysis = self.model.get_analysis_for_track(artist_name,track_name)
        #resetting the seed makes the same "random" numbers appear each time
        features =  track_analysis[['Track duration','Tempo','Max Key']]
        #print(features.to_string())

        data = scale(features)
        #print(data)
        #print("Mean:" + str(data.mean(axis=0)))
        #print("STD:"+str(data.std(axis=0)))

        k = 3

        #reduces number of features to two dimensions
        #only useful for 2d figure
        reduced_data = PCA(n_components=2).fit_transform(data)
        # Step size of the mesh. Decrease to increase the quality of the VQ.
        h = 0.02  # point in the mesh [x_min, m_max]x[y_min, y_max].

        # Plot the decision boundary. For that, we will assign a color to each
        x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
        y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        plt.figure(0,figsize=(5.841, 9.195), dpi=100)
        #clear figure
        plt.clf()

        plt.suptitle(
            "Comparing multiple K-Medoids metrics to K-Means and each other",
            fontsize=14,
        )

        selected_models = [
           # (
           #     KMedoids(metric="manhattan", n_clusters=k),
           #     "KMedoids (manhattan)",
           # ),
            #(
             #   KMedoids(metric="euclidean", n_clusters=k),
             #   "KMedoids (euclidean)",
            #)#,
           # (KMedoids(metric="cosine", n_clusters=k), "KMedoids (cosine)"),
            (KMeans(n_clusters=k), "KMeans") #,
        ]

        plot_rows = int(np.ceil(len(selected_models) / 2.0))
        plot_cols = 2

        for i, (model, description) in enumerate(selected_models):
            # Obtain labels for each point in mesh. Use last trained model.
            model.fit(reduced_data)
            Z = model.predict(np.c_[xx.ravel(), yy.ravel()])

            # Put the result into a color plot
            Z = Z.reshape(xx.shape)
            plt.subplot(plot_cols, plot_rows, i + 1)
            plt.imshow(
                Z,
                interpolation="nearest",
                extent=(xx.min(), xx.max(), yy.min(), yy.max()),
                cmap=plt.cm.Paired,
                aspect="equal",
                origin="lower",
            )

            plt.plot(
                reduced_data[:, 0], reduced_data[:, 1], "k.", markersize=1, alpha=0.3
            )
            # Plot the centroids as a white X
            centroids = model.cluster_centers_
            plt.scatter(
                centroids[:, 0],
                centroids[:, 1],
                marker="x",
                s=169,
                linewidths=3,
                color="w",
                zorder=10,
            )
            plt.title(description)
            plt.xlim(x_min, x_max)
            plt.ylim(y_min, y_max)
            plt.xticks(())
            plt.yticks(())

        #isolatve track tempos
        plt.savefig('clusters.png', dpi= 192)

        Sum_of_squared_distances = []

        mean_silhouette_scores = []
        #finding ideal k using elbow method
        K = range(3, 15)
        for k in K:
            km = KMedoids(n_clusters=k)
            km = km.fit(data)
            if k == 3:
                indeces = []
                print("CLUSTER CENTRES:"+str(km.cluster_centers_))
                for centre in km.cluster_centers_.tolist():
                    indeces.append((data.tolist()).index(centre)+1)
                for index in indeces:
                    print(index)
            Sum_of_squared_distances.append(km.inertia_)

            km = KMeans(n_clusters=k, random_state=0).fit_predict(data)

            # Compute the silhouette scores for each sample FOR THIS k_medoids
            sample_silhouette_values = silhouette_samples(data, km)
            if k == 3:
                print(sample_silhouette_values)
                min = +2
                for index,sample in enumerate(sample_silhouette_values):
                     if sample < min:
                         min_id = index
                         min = sample
                     print("index:"+str(index) +" sample "+str(sample))
                print(min_id)
            mean_silhouette_scores.append(statistics.mean(sample_silhouette_values))

        plt.figure(1)
        plt.plot(K, Sum_of_squared_distances, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Sum_of_squared_distances')
        plt.title('Elbow Method For Optimal k')
        plt.savefig('elbow.png')
        plt.figure(2)
        plt.plot(K,mean_silhouette_scores, 'bx-')
        plt.xlabel('k')
        plt.ylabel('silhouette')
        plt.title('Average Silhouette for k = 1,14')
        plt.savefig('silhouette.png')

        #lof = LocalOutlierFactor(novelty=True)
        #lof.fit(data)
        #plt.figure(2)
        #plt.plot(K, Sum_of_squared_distances, 'bx-')
        #plt.xlabel('k')
        #plt.ylabel('Sum_of_squared_distances')
        #plt.title('Elbow Method For Optimal k')
        #plt.savefig('elbow.png')


        #get labels of kmeans
        k_medoids = KMeans(n_clusters=3, random_state=0).fit_predict(data)

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(data, k_medoids)
        print("For k =", k,
              "The average silhouette_score is of KMedoids:", silhouette_avg)

        print(k_medoids)
        k_meds = np.asarray(k_medoids)
        unique_elements, counts = np.unique(k_meds,return_counts= True)
        print(np.asarray((unique_elements,counts)))
        track_analysis['Labels'] = pd.Series(k_medoids, index=track_analysis.index)
        return track_analysis



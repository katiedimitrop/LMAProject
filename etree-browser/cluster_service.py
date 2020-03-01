# part of logic tier: this will transform user queries into SPARQL queries and
# aggregate the results
import pandas as pd
from models import TrackModel
import pandas as pd
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import scale
from sklearn_extra.cluster import KMedoids
class ClusterService:
    def __init__(self):
        self.model = TrackModel()

    def get_analysis_for_track(self, artist_name, track_name):

        track_analysis = self.model.get_analysis_for_track(artist_name,track_name)
        #resetting the seed makes the same "random" numbers appear each time
        features =  track_analysis[['Track duration','Tempo']]
        #print(features.to_string())

        data = scale(features)
        print(data)
        print("Mean:" + str(data.mean(axis=0)))
        print("STD:"+str(data.std(axis=0)))

        k = 5

        #reduces number of features to two dimensions
        #only useful for 2d figure
        reduced_data = data#PCA(n_components=2).fit_transform(data)
        # Step size of the mesh. Decrease to increase the quality of the VQ.
        h = 0.02  # point in the mesh [x_min, m_max]x[y_min, y_max].

        # Plot the decision boundary. For that, we will assign a color to each
        x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
        y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

        plt.figure(0)
        plt.clf()

        plt.suptitle(
            "Comparing multiple K-Medoids metrics to K-Means and each other",
            fontsize=14,
        )

        selected_models = [
            (
                KMedoids(metric="manhattan", n_clusters=k),
                "KMedoids (manhattan)",
            ),
            (
                KMedoids(metric="euclidean", n_clusters=k),
                "KMedoids (euclidean)",
            ),
            (KMedoids(metric="cosine", n_clusters=k), "KMedoids (cosine)"),
            (KMeans(n_clusters=k), "KMeans"),
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
                aspect="auto",
                origin="lower",
            )

            plt.plot(
                reduced_data[:, 0], reduced_data[:, 1], "k.", markersize=2, alpha=0.3
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
        plt.savefig('clusters.png')

        Sum_of_squared_distances = []

        #finding ideal k using elbow method
        K = range(1, 15)
        for k in K:
            km = KMedoids(n_clusters=k)
            km = km.fit(data)
            Sum_of_squared_distances.append(km.inertia_)
        plt.figure(1)
        plt.plot(K, Sum_of_squared_distances, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Sum_of_squared_distances')
        plt.title('Elbow Method For Optimal k')
        plt.savefig('elbow.png')

        lof = LocalOutlierFactor(novelty=True)
        lof.fit(data)
        plt.figure(2)
        plt.plot(K, Sum_of_squared_distances, 'bx-')
        plt.xlabel('k')
        plt.ylabel('Sum_of_squared_distances')
        plt.title('Elbow Method For Optimal k')
        plt.savefig('elbow.png')
        #get labels of kmeans
        k_medoids = KMeans(n_clusters=3, random_state=0).fit_predict(data)
        print(k_medoids)
        k_meds = np.asarray(k_medoids)
        unique_elements, counts = np.unique(k_meds,return_counts= True)
        print(np.asarray((unique_elements,counts)))
        track_analysis['Labels'] = pd.Series(k_medoids, index=track_analysis.index)
        return track_analysis



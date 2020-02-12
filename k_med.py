import numpy as np

# 1.initialization phase
def init_medoids(X, k):
    from numpy.random import choice, seed
    seed(1)
    # Generate a uniform random sample from the range of indexes
    # with length k without replacement (can't pick same index twice)
    samples = choice(len(X), size=k, replace=False)
    # a matrix of the sampled medoids
    return X[samples, :]

# 2.Computing the distance matrix
# no of columns is the number of medoids or clusters()
# no of rows is the number of data points
def compute_d_p(X, medoids, p):
    m = len(X)
    medoids_shape = medoids.shape
    # if 1-d array provided, reshape to single 2d array
    if len(medoids_shape) == 1:
        medoids = medoids.reshape((1, len(medoids)))
    k = len(medoids)

    S = np.empty((m, k))

    for i in range(m):
        d_i = np.linalg.norm(X[i, :] - medoids, ord=p, axis=1)
        S[i, :] = np.around(d_i ** p, 4)
    return S


# 3.Cluster assignment: check for each data point which medoid is closer to it
# and assign it that label
def assign_labels(S):
    return np.argmin(S, axis=1)


# 4.Swap test,
def update_medoids( X, medoids, p):
    # recompute distance matrix
    S = compute_d_p(X, medoids, p)
    labels = assign_labels(S)

    out_medoids = medoids
    # for each cluster
    for i in set(labels):

        avg_dissimilarity = np.sum(compute_d_p(X, medoids[i], p))

        cluster_points = X[labels == i]
        # search if any of the points in the cluster decreases the average
        # dissimilarity coefficient
        for datap in cluster_points:
            new_medoid = datap
            new_dissimilarity = np.sum(compute_d_p(X, new_medoid, p))

            if new_dissimilarity < avg_dissimilarity:
                avg_dissimilarity = new_dissimilarity
                # the point in the cluster which decreases the dissimilarity the most
                # will be chosen
                out_medoids[i] = new_medoid

    return out_medoids


# check whether medoids have changed
def has_converged(old_medoids, medoids):
    return set([tuple(x) for x in old_medoids]) == set([tuple(x) for x in medoids])

    # Full algorithm


def kmedoids(X, k, p, starting_medoids=None, max_steps=np.inf):
    if starting_medoids is None:
        medoids = init_medoids(X, k)
    else:
        medoids = starting_medoids

    converged = False
    labels = np.zeros(len(X))
    i = 1
    while (not converged) and (i <= max_steps):
        old_medoids = medoids.copy()

        S = compute_d_p(X, medoids, p)

        labels = assign_labels(S)

        medoids = update_medoids(X, medoids, p)

        converged = has_converged(old_medoids, medoids)
        i += 1
    return (medoids, labels)
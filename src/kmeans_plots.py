import numpy as np
import matplotlib.pyplot as plt

# %matplotlib inline

from skimage import io, color, filters
from skimage.transform import resize, rotate
from skimage.color import rgb2gray
from sklearn.cluster import KMeans


def create_cluster_scatter(image, k):

    image_shape = image.shape
    X = image.reshape(-1, 4)
    example_X = X[::1000]
    clf = KMeans(n_clusters=k).fit(example_X)

    idx = np.argsort(clf.cluster_centers_.sum(axis=1))
    mask = np.zeros_like(idx)
    mask[idx] = np.arange(k)

    labels = mask[clf.labels_]

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection="3d")

    indices = [i for i in range(k)]

    if len(indices) == 2:
        plt.style.use("ggplot")  # I also like fivethirtyeight'
        plt.rcParams.update({"font.size": 14, "font.family": "sans"})
        ax = fig.add_subplot(111)
        ax.scatter(
            example_X[:, 0], example_X[:, 1], c=labels.astype(float), edgecolor="k"
        )
        ax.set_xlabel("Pixel Intensities", color="black")
        ax.set_ylabel("Pixel Intensities", color="black")
        ax.set_title("KMeans 2 Cluster Classification\n of Pixel Intensities")
    else:
        plt.rcParams.update({"font.size": 14, "font.family": "sans"})
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(
            example_X[:, 0],
            example_X[:, 1],
            example_X[:, 2],
            c=labels.astype(float),
            edgecolor="k",
        )
        ax.set_xlabel("Pixel Intensities", color="black")
        ax.set_ylabel("Pixel Intensities", color="black")
        ax.set_zlabel("Pixel Intensities", color="black")
        ax.set_title("KMeans 3 Cluster Classification\n of Pixel Intensities")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    image = io.imread("./../satellite_imagery/chile/area_8/area_8_2000.png")
    create_cluster_scatter(image, 3)


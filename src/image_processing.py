import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %matplotlib inline

from skimage import io, color, filters
from skimage.transform import resize, rotate
from skimage.color import rgb2gray
from sklearn.cluster import KMeans


def calculate_aerial_coverage(image_dict):
    """
    Scans satellite imagery folder for desired images.
    Runs KMeans clustering on each image to determine aerial snow cover.
    Outputs dictionary with values for each individual area over the desired time period. 
    """

    for area in image_dict.keys():
        area_images = []
        for yr in yrs:
            image = io.imread(
                "./satellite_imagery/chile/{}/{}_{}.png".format(area, area, yr)
            )
            area_images.append(image)

        area_kmeans_images = []
        area_2 = []

        # KMeans clustering
        for image in area_images:
            k = 3
            cluster_2 = 0

            image_shape = image.shape
            X = image.reshape(-1, 4)
            clf = KMeans(n_clusters=k).fit(X)  # looking for the 3 dominant colors

            # ensures "cluster 2" will always be associated with snow cover
            # this is important to ensure accurate comparison of images
            idx = np.argsort(clf.cluster_centers_.sum(axis=1))
            mask = np.zeros_like(idx)
            mask[idx] = np.arange(k)

            for label in mask[clf.labels_]:
                if label == 2:
                    cluster_2 += 1

            prop_cluster2 = cluster_2 / len(mask[clf.labels_])

            area_kmeans_images.append(
                clf.labels_.reshape(image_shape[0], image_shape[1])
            )

            area_2.append(round(prop_cluster2, 2))

            image_dict[area] = area_2

    return image_dict


class YearlyDifferenceToDF:
    """
    Takes input dictionary created from image processing flow (above function).
    Runs calculations for each key in diciontary to determine year over year change in snow cover.
    Outputs data frame, dependent on year over year or absolute values for year over year changes desired.
    Data frames can then be used in hypothesis testing/further analysis as desired.
    """

    def __init__(self, input_dict, type_):
        self.input_dict = input_dict
        self.type_ = type_
        self.dict_to_df = None
        # self.input_list = self.input_dict.keys()

    def yy_difference(self):
        yy_dict = dict()
        for key, value in self.input_dict.items():
            input_list = value
            yy_diffs = []
            for i, snow_cover in enumerate(input_list):
                if i == 0:
                    yy_diffs.append(0)
                else:
                    if self.type_ == "yy":
                        diff = round(input_list[i] - input_list[i - 1], 2)
                    else:
                        diff = round(abs(input_list[i] - input_list[i - 1]), 2)
                    yy_diffs.append(diff)
            yy_dict[key] = yy_diffs
        self.dict_to_df = yy_dict

    def create_df(self):
        new_df = pd.DataFrame(self.dict_to_df)
        new_df.set_index(np.arange(1984, 2017), inplace=True)
        return new_df


if __name__ == "__main__":
    yrs = np.arange(1984, 2017)
    area_nums = np.arange(1, 21)

    areas = {
        "area_1": [],
        "area_2": [],
        "area_3": [],
        "area_4": [],
        "area_5": [],
        "area_6": [],
        "area_7": [],
        "area_8": [],
        "area_9": [],
        "area_10": [],
    }

    full_chile_processing = calculate_aerial_coverage(areas)
    df = pd.DataFrame(full_chile_processing)

    types = ["yy", "abs_yy"]

    final_df_list = []
    for i in range(2):
        year_over_year = YearlyDifferenceToDF(full_chile_processing, type_=types[i])
        year_over_year.yy_difference()
        final_df = year_over_year.create_df()
        final_df_list.append(final_df)

    yy_change_df, yy_abs_change_df = final_df_list

    # yy_change_df.to_csv (r'final_df.csv', index=False, header=True)
    # df.to_csv (r'snow_cover_.csv', index=False, header=True)


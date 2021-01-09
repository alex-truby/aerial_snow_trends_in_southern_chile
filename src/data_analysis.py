import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib.pyplot as plt

import ruptures as rpt
from itertools import cycle

from ruptures.utils import pairwise


class AnalyzeData:
    def __init__(self, input_df, input_dict):
        self.input_df = input_df.copy()
        self.input_dict = input_dict
        self.means = None
        self.mean_of_means = None
        self.breakpoint = None

    def weight_and_average(self):
        # input_dict = area_dict
        area_weights_dict = dict()
        total_area_analyzed = sum(self.input_dict.values())
        area_weights_vals = np.array(list(self.input_dict.values())) / float(
            total_area_analyzed
        )

        for area, val in zip(self.input_dict.keys(), area_weights_vals):
            area_weights_dict[area] = val

        self.input_df = self.input_df.mul(
            [val for val in list(area_weights_dict.values())], axis=1
        )

        self.input_df["mean"] = self.input_df.mean(axis=1)

        self.means = list(self.input_df["mean"])
        self.mean_of_means = np.array(self.means).mean()

        return self.means, self.mean_of_means

    def create_bar_chart(self):
        plt.style.use("ggplot")
        plt.rcParams.update({"font.size": 16, "font.family": "sans"})

        x = np.arange(1984, 2017)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.bar(
            x, self.means, label="Weighted Yearly Snow Cover from Imagery", color="navy"
        )

        ax.set_title(
            "Average Yearly Weighted Aerial Snow Cover\n from Imagery 1984-2016",
            color="black",
        )
        ax.plot(
            (1985, 2017),
            (self.mean_of_means, self.mean_of_means),
            "r--",
            label="Average Weighted Aerial Snow Cover 1984 - 2016".format(
                round(self.mean_of_means, 2)
            ),
        )
        ax.set_xlabel("Years", color="black")
        ax.set_ylabel("Weighted Aerial Snowcover, unitless", color="black")
        ax.set_xlim(1984, 2017)
        ax.set_ylim(0.015, 0.021)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def find_changepoint(self):
        binseg_alg = rpt.Binseg(model="l2").fit(np.array(self.means))
        break_point, cost = binseg_alg._single_bkp(0, 33)
        self.breakpoint = break_point
        return self.breakpoint

    def plot_change_point(self):
        # binseg_alg = rpt.Binseg(model="l2").fit(np.array(self.means))
        # binseg_result = binseg_alg.predict(n_bkps=1)
        bkp = self.breakpoint

        signal = np.array(self.means)
        signal = signal.reshape(-1, 1)
        n_samples, n_features = signal.shape

        fig, axs = plt.subplots(figsize=(14, 7))
        axs = [axs]

        for ax, sig in zip(axs, signal.T):
            COLOR_CYCLE = ["#4286f4", "#f44174"]
            color_cycle = cycle(COLOR_CYCLE)
            ax.plot(range(n_samples), sig)

            bkps = 1
            alpha = 0.2

            ax.axvspan(0, bkp, facecolor=COLOR_CYCLE[0], alpha=alpha)
            ax.axvspan(bkp, 32, facecolor=COLOR_CYCLE[1], alpha=alpha)

            color = "k"  # color of the lines indicating the computed_chg_pts
            linewidth = 3  # linewidth of the lines indicating the computed_chg_pts
            linestyle = "--"  # linestyle of the lines indicating the computed_chg_pts

            ax.axvline(x=bkp, color=color, linewidth=linewidth, linestyle=linestyle)

            ax.set_xticks([1, 6, 11, 16, 21, 26, 31])
            ax.set_xticklabels(
                [1985, 1990, 1995, 2000, 2005, 2010, 2015], color="black"
            )

            ax.set_title("Change Point Detection", color="black")
            ax.set_xlabel("Years", color="black")
            ax.set_ylabel("Weighted Aerial Snowcover, unitless", color="black")

        fig.tight_layout()
        plt.show()

    def hypothesis_test(self):
        t, p = stats.ttest_ind(
            self.means[: int(self.breakpoint)],
            self.means[int(self.breakpoint) :],
            equal_var=False,
        )
        return p


if __name__ == "__main__":
    df = pd.read_csv("./../data/snow_cover.csv")
    area_dict = {
        "area_1": 1663,
        "area_2": 1349,
        "area_3": 1276,
        "area_4": 1453,
        "area_5": 1747,
        "area_6": 904,
        "area_7": 910,
        "area_8": 1610,
        "area_9": 1325,
        "area_10": 1870,
    }

    ad = AnalyzeData(df, area_dict)
    means, mean_of_means = ad.weight_and_average()
    ad.create_bar_chart()
    ad.find_changepoint()
    ad.plot_change_point()
    print(ad.hypothesis_test())


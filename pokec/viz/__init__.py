import matplotlib.pyplot as plt
import os
import numpy as np

directory = os.path.abspath(os.path.join(os.path.dirname(__file__)))
plots_dir = f"{directory}/plots"
tables_dir = f"{directory}/tables"


class Viz:

    def __init__(self, pre_cleaning=True):
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)
        if not os.path.exists(tables_dir):
            os.makedirs(tables_dir)
        if pre_cleaning:
            self.status_tag = "(Before Cleaning)"
        else:
            self.status_tag = "(After Cleaning)"

    def bar_plot(self, x, y, xlabel=None, ylabel=None, title=None, degrees=None, color='maroon'):
        plt.bar(x, y, color=color, width=0.4)
        if degrees:
            plt.xticks(rotation=degrees)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f"{title} {self.status_tag}")
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/{title}_{self.status_tag}")
        plt.show()

    def line_plot(self, df, title):
        df.plot()
        plt.title(f"{title} {self.status_tag}")
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/{title}_{self.status_tag}")
        plt.show()

    def hist_plot(self, series, title, xlabel=None, ylabel=None):
        series.hist()
        plt.title(f"{title} {self.status_tag}")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/{title}_{self.status_tag}")
        plt.show()

    def scatter_plot(self, x, y, title, c=None, xlabel=None, ylabel=None):
        plt.scatter(x, y, c=c)
        plt.title(f"{title} {self.status_tag}")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/{title}_{self.status_tag}")
        plt.show()

    def sp_with_legend(self, x, y, cdict, classes, title, xlabel=None, ylabel=None):
        fig, ax = plt.subplots()
        for g in np.unique(classes):
            ix = np.where(classes == g)
            ax.scatter(x.iloc[ix], y.iloc[ix], c=cdict[g], label=g, s=100)
        ax.legend()
        plt.title(f"{title} {self.status_tag}")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/{title}_{self.status_tag}")
        plt.show()

    def grouped_bar_plot(self, df, title, xlabel=None, ylabel=None):
        df.plot(kind='bar')
        plt.title(f"{title} {self.status_tag}")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(f"{plots_dir}/{title}_{self.status_tag}")
        plt.show()

    def export_table_as_csv(self, df, filename):
        df.to_csv(f"{tables_dir}/{filename}_{self.status_tag}.csv", index=False)

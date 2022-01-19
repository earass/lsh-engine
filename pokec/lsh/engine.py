import pandas as pd
from pokec.utils import time_summary
from pokec.cache import Cache
from pokec.viz import Viz
import logging
import numpy as np
from pokec.lsh.base import Grouping


def jaccard_similarity_score(a, b):
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


def bitwise_xor_hash(mask, x):
    return int(x ^ mask)


class LSH(Cache, Grouping, Viz):

    def __init__(self, df, n_hash=10, export=True):
        self.df = df
        self.n_hash = n_hash
        self.shingles_df = pd.DataFrame()
        self.shingle_dict = {}
        self.sig_matrix = pd.DataFrame()
        self.shingle_size = 0
        self.params = None
        self.out = pd.DataFrame()
        self.buckets_index = pd.DataFrame()
        self.export = export
        Cache.__init__(self, pre_cleaning=False)
        Grouping.__init__(self, width=n_hash)
        Viz.__init__(self, pre_cleaning=False)


    @time_summary
    def pre_process(self):
        # creating BMI buckets
        conditions = [
            self.df['BMI'].between(0, 17),
            self.df['BMI'].between(18, 25),
            self.df['BMI'].between(26, 30),
            self.df['BMI'].between(31, 35),
            self.df['BMI'] > 35,
        ]
        choices = ['BMI: 0 - 17', 'BMI: 18 - 25', 'BMI: 26 - 30', 'BMI: 31 - 35', 'BMI: 35+']
        self.df['BMI'] = np.select(conditions, choices, default=None)

        self.df['public'] = self.df['public'].map({1: 'Public', 0: 'Not Public', 1.0: 'Public', 0.0: 'Not Public'})

        self.df['AgeGroup'] = "Age: " + self.df['AgeGroup']

        # removing duplicate or already mapped cols
        cols_to_drop = ['completion_percentage', 'gender', 'last_login', 'registration', 'AGE', 'body',
                        'Height', 'Weight']
        self.df.drop(cols_to_drop, axis=1, inplace=True)

    @time_summary
    def generating_shingles(self):
        self.shingles_df[1] = self.df['user_id']
        self.df.drop('user_id', axis=1, inplace=True)
        self.shingles_df[0] = self.df.apply(frozenset, 1).to_frame()
        self.df = None

    @time_summary
    def compute_jaccard_similarity(self):
        temp_df = self.shingles_df.assign(temp=1)  # adding temp column
        merged_df = temp_df.merge(temp_df, on='temp').drop('temp', 1)
        merged_df.columns = ['A', 'B']
        del temp_df

        fnc = np.vectorize(jaccard_similarity_score)
        y = fnc(merged_df['A'], merged_df['B']).reshape(len(self.df), -1)
        del merged_df

    @time_summary
    def compute_similarity(self):
        np.vectorize(self.add_set)(self.shingles_df[0], self.shingles_df[1])

        clusters = self.get_sets()
        clusters = pd.DataFrame({"Clusters": list(clusters)})
        self.export_df_as_csv(clusters, 'clusters')
        self.export_df_as_csv(clusters, 'hashmap_index')

        cluster_lengths = clusters['Clusters'].apply(len)
        self.hist_plot(cluster_lengths, title="LSH Similarity Buckets Size Histogram",
                       xlabel='Similarity Bucket Size', ylabel='Frequency')

    @time_summary
    def run(self):
        logging.info("Pre processing for LSH")
        self.pre_process()

        logging.info("Generating Shingles")
        self.generating_shingles()

        logging.info("Computing Similarity")
        self.compute_similarity()

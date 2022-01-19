import pandas as pd
import numpy as np
import logging
from pokec.utils import time_summary
from pokec.munging.constants import cp_col
from pokec.cache import Cache


class Cleaning(Cache):

    def __init__(self, df):
        Cache.__init__(self)
        self.df = df
        self.out = pd.DataFrame()

    @time_summary
    def filter_rows(self, n_percentile=0.3):
        """ Filter records based on the completion percentage.
        Records with completion_percentage lower than n_percentile would be removed.
         By default removing records that have less than 30th percentile of completion"""
        threshold = self.out[cp_col].quantile(n_percentile)
        logging.info(f"Completion Percentage Threshold: {threshold}")
        cond = self.out[cp_col] >= threshold
        self.out = self.out[cond]
        logging.info(f"Keeping {len(self.out)} only")

    @time_summary
    def filter_columns(self, n_percentile=0.75):
        """ Filter columns based on the occurrence of missing values.
            Columns with percentage of missing values greater than n_percentile would be removed.
            By default removing records that have greater than 75th percentile of missing values"""
        missing_perc_in_cols = self.read_parquet_df('missing_perc_in_cols')
        threshold = missing_perc_in_cols['MissingPercentage'].quantile(n_percentile)
        logging.info(f"Missing values threshold: {threshold}")
        cond = missing_perc_in_cols['MissingPercentage'] < threshold
        columns_to_keep = missing_perc_in_cols.loc[cond, 'Column'].to_list()
        logging.info(f"Following columns are kept: {', '.join(columns_to_keep)}")
        discarded_cols = [col for col in self.df.columns if col not in columns_to_keep]
        logging.info(f"Following columns are dropped: {', '.join(discarded_cols)}")
        logging.info(f"Column count: {len(columns_to_keep)}")
        self.out = self.df[columns_to_keep]
        # self.out.drop('user_id', axis=1, inplace=True)

    @time_summary
    def map_gender_names(self):
        mapping = {1: 'Male', 0: 'Female', 1.0: 'Male', 0.0: 'Female'}
        self.out['GenderMF'] = self.out['gender'].map(mapping)

    @time_summary
    def get_height_weight(self):
        self.out[['Height', 'Weight']] = self.out["body"].str.split(pat=", ", expand=True)[[0, 1]]
        self.out['Weight'] = np.where(self.out['Height'].str.contains('kg', case=False), self.out['Height'],
                                      self.out['Weight'])
        self.out['Height'] = np.where(self.out['Height'].str.contains('kg', case=False), np.nan, self.out['Height'])
        self.out['Height'] = self.out['Height'].str.replace(r'\D+', '').replace([None, ' ', ''], np.nan).astype(float)
        self.out['Weight'] = self.out['Weight'].str.replace(r'\D+', '').replace([None, ' ', ''], np.nan).astype(float)

        # truncating values above tallest and heaviest persons
        max_height = 272  # tallest person height
        min_height = 100  # tallest person height
        max_weight = 595  # tallest person weight
        min_weight = 30  # tallest person weight

        self.out['Height'] = np.where(self.out['Height'].between(min_height, max_height), self.out['Height'], np.nan)
        self.out['Weight'] = np.where(self.out['Weight'].between(min_weight, max_weight), self.out['Weight'], np.nan)

        self.out['BMI'] = self.out['Weight'] / (self.out['Height'] / 100) ** 2

        # ranging BMI
        self.out['BMI'] = np.where(self.out['BMI'].between(13.6, 50), self.out['BMI'], np.nan)

    @time_summary
    def marital_status_mapping(self):
        conditions = [
            (self.out['marital_status'].str.contains('slobodny', na=False, case=False)) | (
                self.out['marital_status'].str.contains('slobodna', na=False, case=False)),
            self.out['marital_status'].str.contains('mam vazny vztah', na=False, case=False),
            self.out['marital_status'].str.contains('zenaty (vydata)', na=False, case=False),
            self.out['marital_status'].str.contains('rozvedeny(a)', na=False, case=False),
            self.out['marital_status'].str.contains('zasnubeny', na=False, case=False)
        ]
        choices = ['Single', 'In Relationship', 'Married', 'Divorced', 'Engaged']
        self.out['MaritalStatus'] = np.select(conditions, choices, default='Other')

    @time_summary
    def relation_to_smoking_mapping(self):
        conditions = [
            self.out['relation_to_smoking'].str.contains(r'nefajcim|nikdy', na=False, case=False, regex=True),
            self.out['relation_to_smoking'].str.contains('fajcim pravidelne', na=False, case=False),
            self.out['relation_to_smoking'].str.contains('fajcim prilezitostne', na=False, case=False),
            self.out['relation_to_smoking'] == 'fajcim',
        ]
        choices = ['Non Smoker', 'Regular Smoker', 'Occasional Smoker', 'Occasional Smoker']
        self.out['SmokingStatus'] = np.select(conditions, choices, default='Other')

    @time_summary
    def relation_to_alcohol_mapping(self):
        conditions = [
            self.out['relation_to_alcohol'].str.contains(r'pijem prilezitostne|prilezitostne', na=False, case=False, regex=True),
            self.out['relation_to_alcohol'].str.contains(r'abstinent|nepijem|nikdy', na=False, case=False, regex=True),
            self.out['relation_to_alcohol'].str.contains('uz nepijem', na=False, case=False),
            self.out['relation_to_alcohol'].str.contains('pijem pravidelne', na=False, case=False)
        ]
        choices = ['Occasional Drinker', 'Abstinent', 'Former Drinker', 'Regular Drinker']
        self.out['DrinkingStatus'] = np.select(conditions, choices, default='Other')

    def age_group_mapping(self):
        conditions = [
            self.out['AGE'].between(0, 14),
            self.out['AGE'].between(15, 24),
            self.out['AGE'].between(25, 34),
            self.out['AGE'].between(35, 44),
            self.out['AGE'] > 44,
        ]
        choices = ['0 - 14', '15 - 24', '25 - 34', '35 - 44', '45 and above']
        self.out['AgeGroup'] = np.select(conditions, choices, default=None)

    @time_summary
    def run(self):
        logging.info("Filtering columns")
        self.filter_columns()
        logging.info("Filtering rows")
        self.filter_rows()

        logging.info(f"Filtered data shape: {self.out.shape}")

        self.map_gender_names()

        self.get_height_weight()

        self.marital_status_mapping()

        self.relation_to_smoking_mapping()

        self.relation_to_alcohol_mapping()

        self.age_group_mapping()

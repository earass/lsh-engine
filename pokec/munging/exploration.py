import pandas as pd
import numpy as np
import logging
from pokec.utils import time_summary
from pokec.cache import Cache
from pokec.viz import Viz

age = 'AGE'
cp_col = 'completion_percentage'


def get_percentile(series, n):
    return series.quantile(n)


class Exploration(Cache, Viz):

    def __init__(self, df, pre_cleaning=True):
        Cache.__init__(self, pre_cleaning=pre_cleaning)
        Viz.__init__(self, pre_cleaning=pre_cleaning)
        self.df = df
        self.missing_perc_in_cols = pd.DataFrame()
        self.primary_stats = pd.DataFrame()
        self.pre_cleaning = pre_cleaning

    @time_summary
    def check_missing_values_percentage(self):
        missing_perc_in_cols = (self.df.isnull().sum() * 100 / len(self.df)).reset_index()
        missing_perc_in_cols.columns = ['Column', 'MissingPercentage']
        self.save_df_as_parquet(missing_perc_in_cols, 'missing_perc_in_cols')
        self.export_table_as_csv(missing_perc_in_cols, 'missing_perc_in_cols')
        self.bar_plot(
            x=missing_perc_in_cols.iloc[:30]['Column'],
            y=missing_perc_in_cols.iloc[:30]['MissingPercentage'],
            ylabel='Percentage',
            xlabel='Column',
            degrees=90,
            title='Missing Percentage in Columns (Slice 1 of 2)'
        )
        self.bar_plot(
            x=missing_perc_in_cols.iloc[30:]['Column'],
            y=missing_perc_in_cols.iloc[30:]['MissingPercentage'],
            ylabel='Percentage',
            xlabel='Column',
            degrees=90,
            title='Missing Percentage in Columns (Slice 2 of 2)'
        )
        self.missing_perc_in_cols = missing_perc_in_cols

    @time_summary
    def get_primary_stats(self, columns=None):
        """ Getting primary stats for few columns """
        if not columns:
            columns = [age, cp_col]
        stats = self.df[columns].describe().reset_index()
        stats.rename(columns={'index': 'Stat'}, inplace=True)
        self.save_df_as_parquet(stats, 'stats')
        self.export_table_as_csv(stats, 'stats')
        self.primary_stats = stats

    @time_summary
    def completion_percentage_analysis(self):
        """ completion_percentage column indicates the proportion of filled values for the record """
        self.hist_plot(series=self.df[cp_col], title='Completion Percentage Histogram',
                       xlabel='Completion Percentage', ylabel='Frequency')

    @time_summary
    def age_analysis(self):
        self.hist_plot(series=self.df[age], title='Age Histogram',
                       xlabel='Age', ylabel='Frequency')

    @time_summary
    def get_top_regions(self, n=20):
        """ Plotting top n regions and their occurrence count """
        top_regions = self.df['region'].value_counts().head(n).reset_index()
        self.bar_plot(
            x=top_regions['index'],
            y=top_regions['region'],
            ylabel='Count',
            xlabel='Region',
            degrees=90,
            title=f'Region Frequency (Top {n})'
        )

    @time_summary
    def years_since_registration(self):
        self.df['registration'] = self.df['registration'].astype('datetime64')
        self.df['years'] = ((pd.Timestamp.now() - self.df['registration']) / np.timedelta64(1, 'Y')).round(0)
        self.hist_plot(series=self.df['years'], title='Years Since Registration Histogram',
                       xlabel='Year', ylabel='Frequency')

    @time_summary
    def gender_height_weight_analysis(self, n=100000):
        gender_map = {1: 'Male', 0: 'Female', 1.0: 'Male', 0.0: 'Female'}
        gender = self.df['gender'].iloc[:n].map(gender_map)
        gender_col_map = {'Male': 'blue', 'Female': 'red'}

        self.sp_with_legend(x=self.df['Height'].iloc[:n], y=self.df['Weight'].iloc[:n], cdict=gender_col_map,
                            classes=gender,
                            title=f"Height vs Weight ({n} cases)", xlabel='Height (cm)', ylabel='Weight (kg)')

    @time_summary
    def bmi_analysis(self):
        self.hist_plot(series=self.df['BMI'], title='BMI Histogram using Height and Weight',
                       xlabel='BMI', ylabel='Frequency')

    @time_summary
    def gender_based_marital_status(self):
        ms = pd.crosstab(self.df['MaritalStatus'], columns=self.df['GenderMF'])
        self.grouped_bar_plot(ms, title='Gender based Marital Status', xlabel='Marital Status', ylabel='Count')

    @time_summary
    def gender_based_smoking_status(self):
        ms = pd.crosstab(self.df['SmokingStatus'], columns=self.df['GenderMF'])
        self.grouped_bar_plot(ms, title='Gender based Smoking Status', xlabel='Smoking Status', ylabel='Count')

    @time_summary
    def gender_based_drinking_status(self):
        ms = pd.crosstab(self.df['DrinkingStatus'], columns=self.df['GenderMF'])
        self.grouped_bar_plot(ms, title='Gender based Drinking Status', xlabel='Drinking Status', ylabel='Count')

    @time_summary
    def age_based_marital_status(self):
        ms = pd.crosstab(self.df['MaritalStatus'], columns=self.df['AgeGroup'])
        self.grouped_bar_plot(ms, title='Age Group based Marital Status', xlabel='Marital Status', ylabel='Count')

    @time_summary
    def age_based_smoking_status(self):
        ms = pd.crosstab(self.df['SmokingStatus'], columns=self.df['AgeGroup'])
        self.grouped_bar_plot(ms, title='Age Group based Smoking Status', xlabel='Smoking Status', ylabel='Count')

    @time_summary
    def age_based_drinking_status(self):
        ms = pd.crosstab(self.df['DrinkingStatus'], columns=self.df['AgeGroup'])
        self.grouped_bar_plot(ms, title='Age Group based Drinking Status', xlabel='Drinking Status', ylabel='Count')

    @time_summary
    def run(self):
        logging.info("Checking missing values percentage")
        self.check_missing_values_percentage()
        #
        logging.info("Getting primary stats")
        self.get_primary_stats()
        #
        logging.info("Getting completion percentage analysis")
        self.completion_percentage_analysis()
        #
        self.age_analysis()

        self.get_top_regions()

        self.years_since_registration()

        if not self.pre_cleaning:
            self.gender_height_weight_analysis()

            self.bmi_analysis()

            self.gender_based_marital_status()

            self.gender_based_drinking_status()

            self.gender_based_smoking_status()

            self.age_based_marital_status()

            self.age_based_drinking_status()

            self.age_based_smoking_status()

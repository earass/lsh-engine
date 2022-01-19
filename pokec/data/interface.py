import pandas as pd
import os
import logging
from pokec.utils import time_summary

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))

cols = ['user_id', 'public', 'completion_percentage', 'gender', 'region', 'last_login', 'registration', 'AGE', 'body',
        'I_am_working_in_field', 'spoken_languages', 'hobbies', 'I_most_enjoy_good_food', 'pets', 'body_type',
        'my_eyesight', 'eye_color', 'hair_color', 'hair_type', 'completed_level_of_education', 'favourite_color',
        'relation_to_smoking', 'relation_to_alcohol', 'sign_in_zodiac', 'on_pokec_i_am_looking_for', 'love_is_for_me',
        'relation_to_casual_sex', 'my_partner_should_be', 'marital_status', 'children', 'relation_to_children',
        'I_like_movies', 'I_like_watching_movie', 'I_like_music', 'I_mostly_like_listening_to_music',
        'the_idea_of_good_evening', 'I_like_specialties_from_kitchen', 'fun', 'I_am_going_to_concerts',
        'my_active_sports', 'my_passive_sports', 'profession', 'I_like_books', 'life_style', 'music', 'cars',
        'politics', 'relationships', 'art_culture', 'hobbies_interests', 'science_technologies', 'computers_internet',
        'education', 'sport', 'movies', 'travelling', 'health', 'companies_brands', 'more']


class DataInterface:
    sample_data_file = 'sample.txt'
    data_file = 'soc-pokec-profiles.txt'
    column_file = 'columns.txt'

    def __init__(self):
        pass

    @classmethod
    @time_summary
    def read(cls, read_sample):
        logging.info("Reading Data")
        file = cls.data_file
        if read_sample:
            file = cls.sample_data_file
        try:
            df = pd.read_csv(f"{dir_path}/{file}", delimiter='\t', header=None, names=cols,
                             index_col=False)
            logging.info(f"Raw data shape: {df.shape}")
            return df
        except OSError:
            raise Exception(f"Please add file {file} in the directory: {dir_path}")

    @classmethod
    def get_column_names(cls):
        with open(f"{dir_path}/{cls.column_file}", 'r') as f:
            cols = f.readlines()
        cols = [c.strip('\n') for c in cols]
        return cols

from pokec.data import DataInterface
from pokec.munging import Exploration, Cleaning
from pokec.lsh.engine import LSH
import logging


if __name__ == '__main__':

    logging.info("********************************* Running Pipeline *********************************")

    read_sample = False  # set this flag True if you want to run on a small sample file for testing.
    di = DataInterface()
    raw_data = di.read(read_sample=read_sample)

    logging.info("Data exploration before cleaning")
    exp = Exploration(df=raw_data)
    exp.run()

    logging.info("Data cleaning")
    clean = Cleaning(df=raw_data)
    clean.run()

    filtered_data = clean.out

    logging.info("Data exploration after cleaning")
    exp = Exploration(df=filtered_data, pre_cleaning=False)
    exp.run()

    logging.info("Implementing LSH")
    lsh_obj = LSH(df=filtered_data, n_hash=10)
    lsh_obj.run()



Following are the files details:

pokec/cache: contains code for caching
pokec/data: contains data files (Add the 'soc-pokec-profiles.txt' file in this directory)
pokec/data/interface.py: code for reading the data
pokec/lsh/base.py: base methods for LSH
pokec/lsh/engine.py: code for executing LSH, inherits base class from base.py
pokec/munging/cleaning.py: code for cleaning data
pokec/munging/exploration.py: code for exploratory analysis
pokec/utils/__init__.py: some utility functions
pokec/viz/__init__.py: Visualization utility functions imported in exploration module
pokec/viz/plots: charts are saved in this directory
pokec/viz/tables: tables are saved in this directory

run.py: Imports all the above modules and triggers the pipeline.

requirements.txt: contains all the packages that need to installed prior to running this project

In order to run the code, just run the run.py file.

If you want to run it for testing, a small sample file is present in directory. You can set the read_sample flag as True to run it on the sample dataset

Contact:
i191254@nu.edu.pk

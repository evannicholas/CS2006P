FILES STRUCTURE

Our submission file will contain 5 directories: code, data, images, images_backup, and notebooks. 

code
	This directory contains the scripts for automated operations: 
	- fixdata.py: filter duplicated or inconsistent data, refine data, add columns for further analysis
	  and save processed data in "data" directory
	- generateGraphs.py: create graphs for data analysis and save graphs in "images" directory

data
	This directory contains the data files used for analysis:
	- CometLanding.csv: original provided dataset
	- CometLandingFixed.csv: dataset after data cleaning and refining
	- CometLandingFixed.json: stores "entities_str" field for all entries in dataset, to be used for
	  analysis related to hashtags
	- mask.jpg: used for creating wordcloud for hashtags

images
	This directory contains the image files for the graphs generated with "generateGraphs.py"

images_backup
	This directory serves as backup for images in "images" directory, where in case graphs generated
	with "generateGraphs.py" are not readable due to the use of incompatible version of python/matplotlib/
	other modules, there will still be an expected, readable version for analysis

notebooks
	This directory contains the Jupyter notebook "CometLanding.ipynb" for data analysis and also serves as 
	the report of this project.

Note: we use anaconda which supplies Jupyter notebook. Thus, most of the libraries are already installed, 
such as matplotlib.


INSTRUCTION

The following(s) are the modules to be installed for running the scripts and notebook along with their
installation command:
 	1. Wordcloud - pip install wordcloud
	2. matplotlib - pip install matplotlib - ENSURE THIS VERSION IS 3.5.1
	3. networkx - pip install networkx - ENSURE THIS VERSION IS 2.6.3
	4. seaborn - pip install seaborn
	5. pandas - pip install pandas
Note: 2. is optional as the scripts can be run without this installation, more specifically this particular
      version of matplotlib if matplotlib is already installed.  However, not installing this version may
	  cause the graphs generated to have unexpected result such as missing headings with error.  During
	  development this version seems to give rise to the least unexpected result, so it is highly 
	  recommended to install this possibly older version.

To perform the automated data cleaning and refining:
1. move current directory to "code"
2. run command: chmod 755 fixdata.py
3. run command: ./fixdata.py CometLanding.csv
--> This should result in creation/overwriting of "CometLandingFixed.csv" and CometLandingFixed.json"
    in "data" directory

To generate graphs for data analysis based on the refined data:
1. move current directory to "code"
2. run command: chmod 755 generateGraphs.py
3. run command: ./generateGraphs.py CometLandingFixed
--> This should result in creation/overwriting of the image files in "images" directory.  Please note that
    the script may take more than 2 hours for running, mainly due to the visualization of the retweet
	network and mentions network which involves large amounts of edges and nodes.
--> Please do NOT run any other scripts or notebooks when running generateGraphs.py, as this may cause the
    kernel to crash
--> Use Google Chrome or Firefox.
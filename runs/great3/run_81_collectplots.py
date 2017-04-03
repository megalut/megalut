"""
A little helper to collect checkplots into one single directory, for easier visualization
"""

import config
import os
import shutil


import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)
logger = logging.getLogger(__name__)



destdirname = "summary_plots"
destdirpath = config.great3.path(destdirname)
if not os.path.isdir(destdirpath):
	os.makedirs(destdirpath)


for subfield in config.great3.subfields:
	
	logger.info("Working on subfield {}".format(subfield))
	
	#origpath = config.great3.subpath(subfield, "ml", "tw-200c-1000r", "ada4s2w_sum33wmassshort_summary.png")
	#newname = "s2_{}.png".format(subfield)
	
	origpath = config.great3.subpath(subfield, "ml", "tw-200c-1000r", "ada4s1w_sum33wmassshort_summary.png")
	newname = "s1_{}.png".format(subfield)
	
	
	destpath = os.path.join(destdirpath, newname)
	
	shutil.copy(origpath, destpath)
	
	

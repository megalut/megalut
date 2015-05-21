"""
Helper functions for plots
"""

import numpy as np
from .. import tools

import logging
logger = logging.getLogger(__name__)


def getdata(cat, features):
	"""
	Extracts the data that can be plotted, skipping all rows with masked content.
	
	:param cat: an astropy table
	:param features: a list of Feature objects
	
	:returns: a table containing only the available rows and required columns. 
	
	"""
	# Potentially, these columns can exist:	
	colnames = []
	for feature in features:
		colnames.append(feature.colname)
		if feature.errcolname != None:
			colnames.append(feature.errcolname)
	
	colnames = list(set(colnames)) # To ensure that they are unique
	
	# We get rid of rows with masked content:
	nomaskcat = tools.table.cutmasked(cat, colnames, keep_all_columns=False)
	# Indeed for plots we don't need the other columns !
	# It's safer to remove them.
	
	return nomaskcat

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
	
	The function returns a dict with keys equal to the colnames and errcolnames of the given features,
	and the columns (aka numpy array) of the same size as corresponding values.
	For every feature, this dict contains both colname and errcolname, with the value of errcolname being None
	if this feature had no errcolname.
	
	"""
	# Potentially, these columns can exist:	
	colnames = []
	for feature in features:
		colnames.append(feature.colname)
		if feature.errcolname != None:
			colnames.append(feature.errcolname)
	
	# We get rid of rows with masked content:
	nomaskcat = tools.table.cutmasked(cat, colnames, keep_all_columns=False)
	
	return nomaskcat

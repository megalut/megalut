"""
Compute some handy derived quantities from adamom measurements.
"""

import astropy.table
import numpy as np
import copy

import logging
logger = logging.getLogger(__name__)

def measfct(catalog, prefix="", **kwargs):
	"""
	We compute 3 new columns:
	- adamom_logflux
	- adamom_g
	- adamom_theta
	"""
	
	cols = ["adamom_flux"]
	for col in cols:
		if col not in catalog.colnames:
			raise RuntimeError("I need column {}".format(col))
			
	output = astropy.table.Table(copy.deepcopy(catalog), masked=True)
	
	output["adamom_logflux"] = np.ma.log10(output["adamom_flux"]) # Negative values get masked.
	
	output["adamom_g"] = np.ma.hypot(output["adamom_g1"], output["adamom_g2"])
	output["adamom_theta"] = 0.5 * np.arctan2(output["adamom_g2"], output["adamom_g1"])
	
	return output
	
	
	
	
	

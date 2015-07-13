"""
This measfct adds a SNR to the catalog, computed from existing columns.
It does not measure the images.

"""

import astropy.table
import numpy as np
import copy

import logging
logger = logging.getLogger(__name__)

def measfct(catalog, prefix="", fluxcol="adamom_flux", sigmacol="adamom_sigma", stdcol="skymad", gain=1.0):
	"""
	We assume here that the images are in ADU, and that 
	gain is given in electron / ADU.
	
	
	:param fluxcol:
	:param sigmacol:
	:param stdcol:
	:param gain:
	
	
	"""
	logger.info("Now computing SNR assuming a gain of {0:.2} electrons per ADU.".format(gain))
	
	output = astropy.table.Table(copy.deepcopy(catalog), masked=True)
	
	sourcefluxes = output[fluxcol] * gain
	
	skynoisefluxes = (output[stdcol] * gain) ** 2 # per pixel
	
	areas = np.pi * output[sigmacol] ** 2 # Should we multiply this by 0.674490 to go from sigma to half-light-rad ?
	
	noises = np.sqrt(sourcefluxes + areas * skynoisefluxes)
	
	snrcol = prefix + "snr"
	
	output[snrcol] = sourcefluxes / noises
	
	return output
	
	
	
	
	

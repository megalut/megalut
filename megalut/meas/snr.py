"""
This measfct adds a SNR to the catalog, computed from existing columns.
It does not measure the images.

"""

import astropy.table
import numpy as np
import copy

import logging
logger = logging.getLogger(__name__)

def measfct(catalog, prefix="", fluxcol="adamom_flux", sigmacol="adamom_sigma", stdcol="skymad", gain=None, gaincol=None):
	"""
	We assume here that the images are in ADU, and that 
	gain is given in electron / ADU.
	
	:param fluxcol:
	:param sigmacol:
	:param stdcol:
	:param gain:
	:param gaincol:
	
	"""
	
	
	if gain != None and gaincol != None:
		raise RuntimeError("Please provide either gain or gaincol, not both!")
		
	output = astropy.table.Table(copy.deepcopy(catalog), masked=True)
	
	if gain != None:
		logger.info("Now computing SNR assuming a gain of {0:.2} electrons per ADU.".format(gain))	
		sourcefluxes = output[fluxcol] * gain
		skynoisefluxes = (output[stdcol] * gain) ** 2 # per pixel
	
	elif gaincol != None:
		logger.info("Now computing SNR using the gain from column '{}'".format(gaincol))	
		sourcefluxes = output[fluxcol] * output[gaincol]
		skynoisefluxes = (output[stdcol] * output[gaincol]) ** 2 # per pixel
	
	else:
		raise RuntimeError("Please provide a gain or gaincol!")
		
	
	areas = np.pi * output[sigmacol] ** 2 # Should we multiply this by 0.674490 to go from sigma to half-light-rad ?
	
	noises = np.sqrt(sourcefluxes + areas * skynoisefluxes)
	
	snrcol = prefix + "snr"
	
	output[snrcol] = sourcefluxes / noises
	
	return output
	
	
	
	
	

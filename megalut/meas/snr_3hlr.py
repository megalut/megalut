"""
This measfct adds a SNR to the catalog, computed from existing columns.
It does not measure the images.

"""

import astropy.table
import numpy as np
import copy

import logging
logger = logging.getLogger(__name__)

def measfct(catalog, prefix="", fluxcol="adamom_flux", sigmacol="adamom_sigma", stdcol="skymad", sizecol=None, gain=None, gaincol=None):
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
		gain = np.abs(gain)
		logger.info("Now computing SNR assuming a gain of {0:.2} electrons per ADU.".format(gain))	
		sourcefluxes = output[fluxcol] * gain
		skynoisefluxes = (output[stdcol] * gain) ** 2 # per pixel
	
	elif gaincol != None:
		logger.info("Now computing SNR using the gain from column '{}'".format(gaincol))	
		gain = np.abs(output[gaincol])
		sourcefluxes = output[fluxcol] * gain
		skynoisefluxes = (output[stdcol] * gain) ** 2 # per pixel
	
	else:
		raise RuntimeError("Please provide a gain or gaincol!")
		
	
	if sizecol is None:
		areas = np.pi * (output[sigmacol] * 3. * 1.177) ** 2 # 1.177sigma = r half light
	else: 
		areas = output[sizecol]
	
	sourcefluxesN = sourcefluxes#0.
	noises = np.sqrt(sourcefluxesN + areas * skynoisefluxes)
	
	snrcol = prefix + "snr"
	
	output[snrcol] = sourcefluxes / noises
	
	return output
	
	
	
	
	

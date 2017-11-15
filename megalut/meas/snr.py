"""
This measfct adds a SNR to the catalog, computed from existing columns.
It does not measure the images.

"""

import astropy.table
import numpy as np
import copy

import logging
logger = logging.getLogger(__name__)

def measfct(catalog, prefix="", fluxcol="adamom_flux", sigmacol="adamom_sigma", stdcol="skymad", sizecol=None, gain=None, gaincol=None, aper=3.0):
	"""
	We assume here that the images are in ADU, and that 
	gain is given in electron / ADU.
	
	:param fluxcol:
	:param sigmacol:
	:param stdcol:
	:param gain:
	:param gaincol:
	
	:param aper: the radius of the effective area is hlr * aper. So aper = 3, the default value, means an aperture with a diameter of 3 times the half-light-diameter.
		This gives values close to FLUX_AUTO / FLUXERR_AUTO
	
	
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
		areas = np.pi * (output[sigmacol] * aper * 1.1774) ** 2 # 1.1774 x sigma = r half light
	else: 
		areas = output[sizecol]
	
	noises = np.sqrt(sourcefluxes + areas * skynoisefluxes)
	
	snrcol = prefix + "snr"
	
	output[snrcol] = sourcefluxes / noises
	
	return output
	
	
	
	
	

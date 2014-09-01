"""
Shape measurement with GalSim's adaptive moments (from its "hsm" module).
"""

import numpy as np
import sys, os
import copy
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import astropy.table
import galsim


def measure(imgfilepath, catalog, stampsize=100, prefix="mes_adamom"):
	"""
	I use the positions "x" and "y" of the input table to extract postage stamps from the image and measure their shapes.
	I return a copy of your input catalog with the new columns appended. One of these colums is the flag:
	
	* 0: OK
	* 1: stamp is not fully within image
	* 2: galsim centroid failed (distance > 10 pixels...)
	* 3: galsim failed
	
	:param imgfilepath: FITS image
	:param catalog: astropy table of objects that I should measure
	:param stampsize: width = height of stamps
	:param prefix: a string to prefix the field names that I'll write
	
	:returns: astropy table
	
	"""
	
	assert int(stampsize)%2 == 0 # checking that it's even
	
	starttime = datetime.now()
	logger.info("Measuring shapes on %s..." % (os.path.basename(imgfilepath)))
	
	# We read in the imgfile. Using only galsim, this is new (and should be checked) !
	bigimg = galsim.fits.read(imgfilepath)
	bigimg.setOrigin(0,0)
	(bigxmin, bigxmax, bigymin, bigymax) = (bigimg.getXMin(), bigimg.getXMax(), bigimg.getYMin(), bigimg.getYMax())
	logger.warning("The origin and stampsize conventions are new and should be tested !")
	
	# We prepare an output table with all the required columns
	output = copy.deepcopy(catalog)
	output.add_columns([
		astropy.table.Column(name=prefix+"_flag", data=np.zeros(len(output), dtype=int)),
		astropy.table.Column(name=prefix+"_flux", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_x", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_y", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_g1", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_g2", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_sigma", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"_rho4", dtype=float, length=len(output))
	])
	
	# We could have boolean columns:
	#astropy.table.Column(name=prefix+"_ok", data=np.zeros(len(output), dtype=bool))
	# One could use MaskedColumn here !
	#astropy.table.MaskedColumn(name="mes_adamom_flux", dtype=float, length=len(output), fill_value=-1)
	
	# Let's save something useful to the meta dict
	output.meta[prefix + "_imgfilepath"] = imgfilepath
	
	# And loop
	for gal in output:
	
		x = gal["x"]
		y = gal["y"]
		
		xmin = int(np.floor(x)) - int(stampsize)/2 + 1
		xmax = int(np.floor(x)) + int(stampsize)/2
		ymin = int(np.floor(y)) - int(stampsize)/2 + 1
		ymax = int(np.floor(y)) + int(stampsize)/2
			
		assert ymax - ymin == stampsize - 1
		assert xmax - xmin == stampsize - 1
	
		# We check that these bounds are fully within the image
		#print xmin, xmax, ymin, ymax
		if xmin < 0 or xmax > bigxmax+1 or ymin < 0 or ymax > bigymax+1:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"_flag"] = 1
			continue
		
		# We prepare the stamp
		bounds = galsim.BoundsI(xmin, xmax, ymin, ymax)
		gps = bigimg[bounds] # galaxy postage stamp
		assert gps.array.shape == (stampsize, stampsize)
		
		# We measure the moments... galsim may fail from time to time, hence the try:
		try:
			res = galsim.hsm.FindAdaptiveMom(gps)
			
		except:
			# This is awesome, but clutters the output 
			#logger.exception("GalSim failed on: %s" % (str(gal)))
			logger.debug("GalSim failed on:\n %s" % (str(gal)))	
			gal[prefix + "_flag"] = 3	
			continue
		
		gal[prefix+"_flux"] = res.moments_amp
		gal[prefix+"_x"] = res.moments_centroid.x
		gal[prefix+"_y"] = res.moments_centroid.y
		gal[prefix+"_g1"] = res.observed_shape.g1
		gal[prefix+"_g2"] = res.observed_shape.g2
		gal[prefix+"_sigma"] = res.moments_sigma
		gal[prefix+"_rho4"] = res.moments_rho4

		# If we made it so far, we check that the centroid is roughly ok:
		if np.hypot(x - gal[prefix+"_x"], y - gal[prefix+"_y"]) > 10.0:
			gal[prefix + "_flag"] = 2
		
	
	endtime = datetime.now()	
	
	n = len(output)
	nfailed = np.sum(output[prefix+"_flag"] > 0)
	
	logger.info("I failed on %i out of %i sources (%.1f percent)" % (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	return output
		

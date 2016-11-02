"""
Simple self-coded moments, for tests and playing around.
In theory, no need for galsim here.
"""

import numpy as np
import copy
from .. import tools

import astropy
import astropy.table

import logging
logger = logging.getLogger(__name__)

def measfct(cat, runon="img", prefix="mom_", xname="x", yname="y", stampsize=100):
	"""
	
	:param runon: "img" or "psf" or ... -- decides on which image this should run.
		You might want to adjust the prefix accordingly.
	:param prefix: a prefix for the new column names. By default, no prefix is used.
	:param xname: name of the column containing the x center around which to measure
	:param yname: idem for y
		
	"""
	
	
	#img = astropy.io.fits.getdata(cat.meta[runon].filepath) # a 2d numpy array
	
	# We load the image:
	img = cat.meta[runon].load()


	# Prepare the catalog: THIS SHOULD BE REVIEWED ONCE WE ALL ADOPT ASTROPY 1.0 AND A RECENT NUMPY !
	cat = astropy.table.Table(copy.deepcopy(cat), masked=True) # Convert the table to a masked table
	# A bit stange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.

	cat.add_columns([
		astropy.table.MaskedColumn(name=prefix+"x", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"y", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"e1", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"e2", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"r", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"flag", dtype=float, length=len(cat)),
	])
	for col in ["x", "y", "e1", "e2", "r", "flag"]:
		cat[prefix+col].mask = [True] * len(cat)
	
	
	
	# Preparing a weight function, and some often reused terms
	
	(xes, yes) = np.mgrid[0:stampsize, 0:stampsize] + 1.0 # The value of the first pixel goes with coordinates (1, 1). That's our convention.
	weights = np.ones((stampsize, stampsize), dtype=float)
	centerdists = np.hypot((xes - (stampsize/2.0 + 0.5)), (yes - (stampsize/2.0 + 0.5)))
	sigma = 5
	weights = np.exp((-1.0 * centerdists**2) / (2.0 * sigma**2))
	
	
	# And now the loop
	for gal in cat:
		
		# Some simplistic progress indication:
		if gal.index%1000 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(len(cat)), gal.index, len(cat)))
		
		(x, y) = (gal[cat.meta[runon].xname], gal[cat.meta[runon].yname])
		(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
		
		if flag != 0:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"flag"] = flag
			continue
		
		else:
			
			array = gps.array.transpose()
			array *= weights
			#print array.shape
			
			assert array.shape == (stampsize, stampsize)
			
			sumarray = np.sum(array)
				
			xmean = np.sum(xes * array) / sumarray
			ymean = np.sum(yes * array) / sumarray
			
			qxx = np.sum(array * (xes - xmean)**2) / sumarray
			qyy = np.sum(array * (yes - ymean)**2) / sumarray
			qxy = np.sum(array * (xes - xmean) * (yes - ymean)) / sumarray
			
			
			# Following the GREAT8 handbook...
			
			if ((qxx * qyy) - qxy**2) < 0.0:
				gal[prefix+"flag"] = 10
				continue
				
			edenum = qxx + qyy + 2.0*np.sqrt((qxx * qyy) - qxy**2)
			e1 = (qxx - qyy) / edenum
			e2 = 2.0 * qxy / edenum
			
			# and 
	
			r = np.sqrt(qxx**2 + qyy**2)
			
			
			xmean -= stampsize/2.0
			ymean -= stampsize/2.0
			
			gal[prefix + "x"] = xmean
			gal[prefix + "y"] = ymean
			gal[prefix + "e1"] = e1
			gal[prefix + "e2"] = e2
			gal[prefix + "r"] = r
			
	nfailed = np.sum(cat[prefix + "flag"] >= 10)
	if nfailed != 0:
		logger.warning("The moment computation failed on %i out of %i sources (%.1f percent)" % (nfailed, len(cat), 100.0*float(nfailed)/float(len(cat))))

	
	return cat


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

from .. import tools



def measure(img, catalog, xname="x", yname="y", stampsize=100, measuresky=True, prefix="adamom_"):
	"""
	Use the pixel positions provided via the 'catalog' input table to extract
	postage stamps from the image and measure their shape parameters.
	Returns a copy of your input catalog with the new (masked) columns appended.
	One of these colums (the only one that is not masked) is the flag:
	
	* 0: OK
	* 1: stamp is not fully within image
	* 2: galsim centroid failed (distance > 10 pixels...)
	* 3: galsim failed
	
	:param img: either the path to a FITS image, or a galsim image object
	:param catalog: astropy table of objects to be measured
	:param psfimg, psfxname, psfyname: (unused)
	:param xname: column name containing the x coordinates in pixels
	:param yname: idem for y
	:param stampsize: width = height of stamps, has to be even
	:type stampsize: int
	:param measuresky: set this to False if you don't want me to measure the sky (edge of stamps)
	:param workdir: path where any possible output files are kept.
	:param prefix: a string to prefix the field names that I'll write
	
	:returns: masked astropy table
	
	"""
	
	if type(img) is str:
		logger.debug("You gave me a filepath, and I'm now loading the image...")
		img = tools.image.loadimg(img)
	
	if "stampsize" in catalog.meta:
		if stampsize != catalog.meta["stampsize"]:
			logger.warning("Measuring with stampsize=%i, but stamps have been generated with stampsize=%i" %\
				(stampsize, catalog.meta["stampsize"]))
			

	if int(stampsize)%2 != 0:
		raise RuntimeError("stampsize should be even!")

	starttime = datetime.now()
	logger.info("Starting shape measurements on %ix%i stamps" % (stampsize, stampsize))
	
	# We prepare an output table with all the required columns
	output = astropy.table.Table(copy.deepcopy(catalog), masked=True) # Convert the table to a masked table
	# A bit stange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.
	
	output.add_columns([
		astropy.table.Column(name=prefix+"flag", data=np.zeros(len(output), dtype=int)), # We will always have a flag
		astropy.table.MaskedColumn(name=prefix+"flux", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"x", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"y", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"g1", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"g2", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"sigma", dtype=float, length=len(output)),
		astropy.table.MaskedColumn(name=prefix+"rho4", dtype=float, length=len(output))
	])
	# By default, all these entries are masked:
	for col in ["flux", "x", "y", "g1", "g2", "sigma", "rho4"]:
		output[prefix+col].mask = [True] * len(output)
	
	# Similarly, we prepare columns for the sky stats:
	if measuresky:
		output.add_columns([
			astropy.table.MaskedColumn(name=prefix+"skystd", dtype=float, length=len(output)),
			astropy.table.MaskedColumn(name=prefix+"skymad", dtype=float, length=len(output)),
			astropy.table.MaskedColumn(name=prefix+"skymean", dtype=float, length=len(output)),
			astropy.table.MaskedColumn(name=prefix+"skymed", dtype=float, length=len(output))
		])
		for col in ["skystd", "skymad", "skymean", "skymed"]:
			output[prefix+col].mask = [True] * len(output)
	
	# Let's save something useful to the meta dict
	output.meta[prefix + "xname"] = xname
	output.meta[prefix + "yname"] = yname
	
	# We do not store this long string here, as it leads to problems when saving the cat to FITS
	#output.meta[prefix + "imgfilepath"] = img.origimgfilepath
	
	n = len(output)
	
	# And loop
	for gal in output:
		
		# Some simplistic progress indication:
		if gal.index%5000 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(n), gal.index, n))
		
		(x, y) = (gal[xname], gal[yname])
		(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
		
		
		if flag != 0:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"flag"] = flag
			# We can't do anything, and we just skip this galaxy.
			continue
		
		
		# If the getting the stamp worked fine, we can for sure 
		# estimate the sky noise and other stats:
		if measuresky:
			out = skystats(gps)
			gal[prefix + "skystd"] = out["std"]
			gal[prefix + "skymad"] = out["mad"]
			gal[prefix + "skymean"] = out["mean"]
			gal[prefix + "skymed"] = out["med"]
		
		# And now we measure the moments... galsim may fail from time to time, hence the try:
		try:
			res = galsim.hsm.FindAdaptiveMom(gps)
			
		except:
			# This is awesome, but clutters the output 
			#logger.exception("GalSim failed on: %s" % (str(gal)))
			# So insted of logging this as an exception, we use debug, but include the tarceback :
			logger.debug("GalSim failed on:\n %s" % (str(gal)), exc_info = True)	
			gal[prefix + "flag"] = 3	
			continue
		
		gal[prefix+"flux"] = res.moments_amp
		gal[prefix+"x"] = res.moments_centroid.x + 1.0 # Not fully clear why this +1 is needed. Maybe it's the setOrigin(0, 0).
		gal[prefix+"y"] = res.moments_centroid.y + 1.0 # But I would expect that GalSim would internally keep track of these origin issues.
		gal[prefix+"g1"] = res.observed_shape.g1
		gal[prefix+"g2"] = res.observed_shape.g2
		gal[prefix+"sigma"] = res.moments_sigma
		gal[prefix+"rho4"] = res.moments_rho4

		# If we made it so far, we check that the centroid is roughly ok:
		if np.hypot(x - gal[prefix+"x"], y - gal[prefix+"y"]) > 10.0:
			gal[prefix + "flag"] = 2
		

	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"flag"] > 0)
	
	logger.info("I failed on %i out of %i sources (%.1f percent)" % (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	return output



def mad(nparray):
	"""
	The Median Absolute Deviation
	http://en.wikipedia.org/wiki/Median_absolute_deviation
	
	Multiply this by 1.4826 to convert into an estimate of the Gaussian std.
	"""

	return np.median(np.fabs(nparray - np.median(nparray)))



def skystats(stamp):
	"""
	I measure some statistics of the pixels along the edge of an image or stamp.
	Useful to measure the sky noise, but also to check for problems. Use "mad"
	directly as a robust estimate the sky std.
	
	:param stamp: a galsim image, usually a stamp
	
	:returns: a dict containing "std", "mad", "mean" and "med"
		Note that "mad" is already rescaled by 1.4826 to be comparable with std.
	
	"""
	
	a = stamp.array
	edgepixels = np.concatenate([
		a[0,1:], # left
		a[-1,1:], # right
		a[:,0], # bottom
		a[1:-1,-1] # top
		])
	assert len(edgepixels) == 2*(a.shape[0]-1) + 2*(a.shape[0]-1)
	
	
	# And we convert the mad into an estimate of the Gaussian std:
	return {
		"std":np.std(edgepixels), "mad": 1.4826 * mad(edgepixels), 
		"mean":np.mean(edgepixels), "med":np.median(edgepixels)
		}
	
	
	

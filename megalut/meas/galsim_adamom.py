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

import utils
from .. import tools


def measfct(catalog, runon="img", stampsize=None, **kwargs):
	"""
	This is a wrapper around galsim_adamom that meets the requirements of a MegaLUT-conform shape measurement function, namely
	to take only one catalog (astropy table) object containing -- or link to -- all the required data.
	In other words, this is a function that you could pass to meas.run.general() etc.
	If you want to combine several shape measurement algorithms into one shot, you would define such a function yourself (not here
	in megalut, but somewhere in your scripts).
	The present measfct serves as an example and is a bit long. It could be kept very short.
	
	:param catalog: an astropy table, which, in this case, is expected to have catalog.meta["img"] set
		to be a megalut.tools.imageinfo.ImageInfo object.
	:param runon: "img" or "psf" or other ImageInfo names to run on.
	:param kwargs: keyword arguments that will be passed to the lower-level measure() function.
		These set parameters of the shape measurement, but they do not pass any data.
		Do not try to specify "img" or "xname" here, it will fail! Set the catalog's meta["img"] instead.
		So for this particular measfct, you probably want to give at least stampsize as kwarg.
	
	"""
	
	# We get the stamp size to use:
	stampsize = catalog.meta[runon].get_stampsize(stampsize)
	
	# We load the image:
	img = catalog.meta[runon].load()

	# And we pass it, with all required kwargs, to the lower-level function:
	return measure(img, catalog, xname=catalog.meta[runon].xname, yname=catalog.meta[runon].yname, stampsize=stampsize, **kwargs)


def measure(img, catalog, xname="x", yname="y", stampsize=None, prefix="adamom_", variant="default"):
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
	:param xname: column name containing the x coordinates in pixels
	:param yname: idem for y
	:param stampsize: width = height of stamps, has to be even
	:type stampsize: int
	:param prefix: a string to prefix the field names that I'll write
	:param variant: a switch for different variants of parameters for this method. 'default' uses defaults,
		'wider' starts failed default-measurements again with a larger sigma and more iterations.
	:type variant: string
	
	
	:returns: masked astropy table
	
	"""
	
	if type(img) is str:
		logger.debug("You gave me a filepath, and I'm now loading the image...")
		img = tools.image.loadimg(img)
	
	if int(stampsize)%2 != 0:
		raise RuntimeError("The stampsize should be even!")

	starttime = datetime.now()
	logger.info("Starting measurements on %ix%i stamps, with variant='%s'" % (stampsize, stampsize, variant))
	
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
	# We want to mask all these entries. They will get unmasked when values will be attributed.
	for col in ["flux", "x", "y", "g1", "g2", "sigma", "rho4"]:
		output[prefix+col].mask = [True] * len(output) # "True" means masked !
		
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
				
		# And now we measure the moments... galsim may fail from time to time, hence the try:
		if variant == "default":
			try: # We simply try defaults:
				res = galsim.hsm.FindAdaptiveMom(gps)
			except:
				# This is awesome, but clutters the output 
				#logger.exception("GalSim failed on: %s" % (str(gal)))
				# So insted of logging this as an exception, we use debug, but include the tarceback :
				logger.debug("HSM with default settings failed on:\n %s" % (str(gal)), exc_info = True)	
				gal[prefix + "flag"] = 3	
				continue # skip to next stamp !
		
		elif variant == "wider":
		
			try:
				try: # First we try defaults:
					res = galsim.hsm.FindAdaptiveMom(gps)
				except: # We change a bit the settings:
					logger.debug("HSM defaults failed, retrying with larger sigma...")
					hsmparams = galsim.hsm.HSMParams(max_mom2_iter=1000)
					res = galsim.hsm.FindAdaptiveMom(gps, guess_sig=15.0, hsmparams=hsmparams)			

			except: # If this also fails, we give up:
				logger.debug("Even the retry failed on:\n %s" % (str(gal)), exc_info = True)	
				gal[prefix + "flag"] = 3	
				continue
		
		else:
			raise RuntimeError("Unknown variant setting '{variant}'!".format(variant=variant))
	
		gal[prefix+"flux"] = res.moments_amp
		gal[prefix+"x"] = res.moments_centroid.x + 1.0 # Not fully clear why this +1 is needed. Maybe it's the setOrigin(0, 0).
		gal[prefix+"y"] = res.moments_centroid.y + 1.0 # But I would expect that GalSim would internally keep track of these origin issues.
		gal[prefix+"g1"] = res.observed_shape.g1
		gal[prefix+"g2"] = res.observed_shape.g2
		gal[prefix+"sigma"] = res.moments_sigma
		gal[prefix+"rho4"] = res.moments_rho4

		# If we made it to this point, we check that the centroid is roughly ok:
		if np.hypot(x - gal[prefix+"x"], y - gal[prefix+"y"]) > 10.0:
			gal[prefix + "flag"] = 2
		

	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"flag"] > 0)
	
	logger.info("I failed on %i out of %i sources (%.1f percent)" % (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	return output

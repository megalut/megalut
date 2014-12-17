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


def measfct(catalog, **kwargs):
	"""
	This is a wrapper around galsim_adamom that meets the requirements of a MegaLUT-conform shape measurement function, namely
	to take only one catalog (astropy table) object containing -- or link to -- all the required data.
	In other words, this is a function that you could pass to meas.run.general() etc.
	If you want to combine several shape measurement algorithms into one shot, you would define such a function yourself (not here
	in megalut, but somewhere in your scripts).
	The present measfct serves as an example and is a bit long. It could be kept very short.
	
	:param catalog: an astropy table, which, in this case, is expected to have catalog.meta["img"] set
		to be a megalut.tools.imageinfo.ImageInfo object.
	:param kwargs: keyword arguments that will be passed to the lower-level measure() function.
		These set parameters of the shape measurement, but they do not pass any data.
		Do not try to specify "img" or "xname" here, it will fail! Set the catalog's meta["img"] instead.
		So for this particular measfct, you probably want to give at least stampsize as kwarg.
	
	"""
	
	# We could have some warnings here.
	# Just to illustrate, an example:
	
	if catalog.meta["img"].stampsize is not None and "stampsize" in kwargs:
		if catalog.meta["img"].stampsize != kwargs["stampsize"]:
			logger.warning("Measuring with stampsize %i, but stamps have been generated with stampsize %i" %\
				(kwargs["stampsize"], catalog.meta["img"].stampsize))
	
	
	# We load the image:
	img = catalog.meta["img"].load()

	# And we pass it, with all required kwargs, to the lower-level function:
	return measure(img, catalog, xname=catalog.meta["img"].xname, yname=catalog.meta["img"].yname, **kwargs)


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
	# We want to mask all these entries. They will get unmasked when values will be attributed.
	for col in ["flux", "x", "y", "g1", "g2", "sigma", "rho4"]:
		output[prefix+col].mask = [True] * len(output) # "True" means masked !
	
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
			out = utils.skystats(gps)
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



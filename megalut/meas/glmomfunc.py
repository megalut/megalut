"""
This module provides a measurement function using FDNT::GLMoment() via the fdnt module that can be
passed to the meas.run wrappers.
"""


import fdnt
import os
import numpy as np
import galsim

import logging
logger = logging.getLogger(__name__)

from datetime import datetime
import copy
import astropy.table
from .. import tools


def measure(img, catalog, xname="x", yname="y", prefix="glmom_", measuresky=True):
	"""
	Use the pixel positions provided via the input table to measure their shape parameters.
	Return a copy of the given catalog, with new columns appended.
	
	:param img: image to be measured
	:param catalog: astropy table of objects to be measured
	:param xname: column name containing the x coordinates in pixels
	:param yname: column name containing the y coordinates in pixels
	:param prefix: a string to prefix the field names that are added to the catalog
	
	:returns: astropy table (the original catalog, with additional columns of measurement values)
	
	"""
	
	starttime = datetime.now()
	
	if type(img) is str:
		logger.debug("You gave me a filepath, and I'm now loading the image...")
		img = tools.image.loadimg(img)
		img.setOrigin(1,1)

	# Prepare an output table with all the required columns
	output = astropy.table.Table(copy.deepcopy(catalog), masked=True) # Convert the table to a masked table
	output.add_columns([
		astropy.table.Column(name=prefix+"flag", data=np.zeros(len(output), dtype=int)),
		astropy.table.Column(name=prefix+"flux", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"x", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"y", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"g1", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"g2", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"sigma", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"rho4", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"snratio", dtype=float, length=len(output)),
	])
	# By default, all these entries are masked:
	for col, col_fill in zip(["flux", "x", "y", "g1", "g2", "sigma", "rho4", "snratio"],
				 [   -1.,  0.,  0., -10., -10.,     -1.,    -1.,        0.]):
		output[prefix+col].mask = [True] * len(output)
		output[prefix+col].fill_value = col_fill

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
	
	# Save something useful to the meta dict
	output.meta[prefix + "xname"] = xname
	output.meta[prefix + "yname"] = yname
	
	n = len(output)
	
	# Loop over each object
	for gal in output:
		
		# Some simplistic progress indication:
		if gal.index%5000 == 0:  # is "index" an astropy table entry?
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(n),
							       gal.index, n))
		# get centroid, size and shear estimates from catalog
		(x, y) = (gal[xname], gal[yname])
		g1g2 = (gal['tru_g1'], gal['tru_g2'])
		size = gal['tru_rad']/0.77741  # gal['tru_rad']/1.17741 is the "true" value;
		                               # this converges better for size ~1 pixel

		# We measure the moments... GLMoment may fail from time to time, hence the try:
		#img.setOrigin(1,1)  # return to normal after megalut.gsutils
		try:
			res = fdnt.GLMoments(img, x, y, size, guess_g1g2=g1g2)

		except RuntimeError, m:
			# NOTE: should never get here.  If it does, re-write fdnt.GLMoments()
			#       such that all exceptions are caught and the failure reasons
			#       reflected in the flags
			print m
			# This is awesome, but clutters the output 
			#logger.exception("GLMoments failed on: %s" % (str(gal)))
			# So insted of logging this as an exception, we use debug, but include
			# the traceback :
			logger.debug("GLMoments failed with %s:\n %s" % (m, str(gal)), exc_info=True)
			#print "GLMoments failed on:\n %s" % (str(gal))
			gal[prefix + "flag"] = -1
			continue

		gal[prefix + "flag"] = res.observed_flags
		try:
			s = galsim.Shear(e1=res.observed_e1, e2=res.observed_e2)
			g1 = s.getG1()
			g2 = s.getG2()
			gal[prefix+"g1"] = g1
			gal[prefix+"g2"] = g2
			gal[prefix+"flux"] = res.observed_b00
			gal[prefix+"x"] = res.observed_centroid.x
			gal[prefix+"y"] = res.observed_centroid.y
			gal[prefix+"sigma"] = res.observed_sigma
			# note: b_22 = rho4-4*rho2+2 = rho4-4*b_11+2*b_00;  b22 is a substitute
			gal[prefix+"rho4"] = res.observed_b22
			gal[prefix + "snratio"] = res.observed_significance

		except ValueError:
			pass  # do nothing, this will "mask" the value out from the astropy table.

		# If we made it so far, we check that the centroid is roughly ok:
		#if np.hypot(x - gal[prefix+"x"], y - gal[prefix+"y"]) > 10.0:
		#	gal[prefix + "flag"] = 2
		
	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"flag"] > 0)
	
	logger.info("GLMoment() failed on %i out of %i sources (%.1f percent)" % \
			    (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % \
			    (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	return output



	
	

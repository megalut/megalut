"""
This module provides a measurement function using FDNT::RunFDNT() via the fdnt module that can be
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
from megalut import tools
from megalut.meas import sewfunc
import sewpy


def measure(img, catalog, xname="x", yname="y", prefix="fdnt_", measuresky=True,
	    sewpy_workdir='sewpy', psf_catalog=None):
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
	
	# RUN SEXTRACTOR MEASUREMENTS
	sexpath = 'sex'
	params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
		  "FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
		  "FWHM_IMAGE", "BACKGROUND", "FLAGS"]
	config = {"DETECT_MINAREA":5, "ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
	sew = sewpy.SEW(sexpath=sexpath, params=params, config=config, workdir=sewpy_workdir, nice=19)
	out = sew(img, assoc_cat=catalog, assoc_xname=xname, assoc_yname=yname, prefix='')
	se_output = out["table"]

	print 'after SExtractor:'   ## DEBUG
	print se_output[:2]  ## DEBUG

	# OPEN ALL NECESSARY FILES
	if type(img) is str:

		psfimg = img.replace('_galimg','_psfimg')  # following the sim naming convention

		logger.debug("Filepath given, loading the corresponding image...")
		img = tools.image.loadimg(img)
		img.setOrigin(0,0)     # for it to work with megalut.tools.image.getstamp()

		psfimg = tools.image.loadimg(psfimg)
		psfimg.setOrigin(0,0)  # for it to work with megalut.tools.image.getstamp()

	# Prepare an output table with all the required columns
	output = astropy.table.Table(copy.deepcopy(se_output), masked=True) # Convert the table to a masked table
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
		astropy.table.Column(name=prefix+"psf_g1", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_g2", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_sigma", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_rho4", dtype=float, length=len(output)),
	])
	# By default, all these entries are masked:
	for col, col_fill in zip(["flux", "x", "y", "g1", "g2", "sigma", "rho4", "snratio",
				  "psf_g1", "psf_g2", "psf_sigma", "psf_rho4"],
				 [   -1.,  0.,  0., -10., -10.,     -1.,    -1.,        0.,
				      -10.,     -10.,         -1.,        -1.]):
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
	
	if psf_catalog is None:
		psfstampsize = catalog.meta["stampsize"]
	else:
		psfstampsize = psf_catalog.meta["stampsize"]
	print
	print 'psfstampsize', psfstampsize
	print

	# Loop over each object
	count = 0  ## DEBUG
	for gal in output:
		
		count += 1  ## DEBUG
		# Some simplistic progress indication:
		if gal.index%5000 == 0:  # is "index" an astropy table entry?
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(n),
							       gal.index, n))
		# get centroid, size and shear estimates from catalog
		(x, y) = (gal[xname], gal[yname])
		g1g2 = (gal['tru_g1'], gal['tru_g2'])
		(a,b,theta) = (gal['AWIN_IMAGE'], gal['BWIN_IMAGE'], gal['THETAWIN_IMAGE'])
		size = gal['tru_rad']/0.77741  # gal['tru_rad']/1.17741 is the "true" value;
		                               # this converges better for size ~1 pixel
		psf_size = 1.5  # (from stampgrid.py, default is round Gaussian PSF of size sigma~1.5)
		psf_size *= 2.0  ## DEBUG TESTING 

		print
		print 'a,b,theta', (a,b,theta)
		print 'g1g2', g1g2
		print

		if gal['assoc_flag'] == False:   # not detected by SExtractor
			continue

		# get the PSF postage stamp image
		# according to megalut.sim.stampgrid, the xy coords are the same as that of galaxies
		(psfstamp, flag) = tools.image.getstamp(x, y, psfimg, psfstampsize)
		psfstamp = psfstamp.copy()   # if I want to move the pixel coords, then I need a copy for RunFDNT() to work
		psfstamp.setOrigin(0,0)
		print 'psf bounds:', psfstamp.getBounds()
		if flag != 0:   # postage stamp extraction unsuccessful
			continue

		# get the galaxy postage stamp image (so much faster!)
		(galstamp, flag) = tools.image.getstamp(x, y, img, psfstampsize)
		galstamp = galstamp.copy()
		print 'gal bounds:', galstamp.getBounds()
		if flag != 0:   # postage stamp extraction unsuccessful
			continue

		# We measure the moments... GLMoment may fail from time to time, hence the try:
		try:
			res = fdnt.RunFDNT(galstamp, psfstamp, x, y, size, psf_size, a, b, theta)

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
			if count >= 3:  break   ## DEBUG
			continue

		gal[prefix + "flag"] = res.intrinsic_flags
		try:
			s = galsim.Shear(e1=res.intrinsic_e1, e2=res.intrinsic_e2)
			g1 = s.getG1()
			g2 = s.getG2()
			gal[prefix+"g1"] = g1
			gal[prefix+"g2"] = g2
			gal[prefix+"flux"] = res.observed_b00
			gal[prefix+"x"] = res.observed_centroid.x
			gal[prefix+"y"] = res.observed_centroid.y
			gal[prefix+"sigma"] = res.intrinsic_sigma
			# note: b_22 = rho4-4*rho2+2 = rho4-4*b_11+2*b_00;  b22 is a substitute
			#gal[prefix+"rho4"] = res.intrinsic_b22
			gal[prefix + "snratio"] = res.observed_significance

		except ValueError:
			pass  # do nothing, this will "mask" the value out from the astropy table.

		# If we made it so far, we check that the centroid is roughly ok:
		#if np.hypot(x - gal[prefix+"x"], y - gal[prefix+"y"]) > 10.0:
		#	gal[prefix + "flag"] = 2
		
		## DEBUG BLOCK
		if count >= 1:
			print output[:2]
			return output

	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"flag"] >= 8)
	
	logger.info("GLMoment() failed on %i out of %i sources (%.1f percent)" % \
			    (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % \
			    (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	print output[:3]  ## DEBUG
	print gal[prefix + "flag"] ## DEBUG
	return output



	
	

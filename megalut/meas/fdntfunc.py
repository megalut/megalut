"""
This module provides a measurement function using FDNT::RunFDNT() via the fdnt module that can be
passed to the meas.run wrappers.
"""


import fdnt
import os, sys
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
from megalut.meas import utils
from .. import tools


def measfct(catalog, runon="img", stampsize=None, **kwargs):
        """
        This is a wrapper around FDNT that meets the requirements of a MegaLUT-conformed shape
	measurement function, namely to take only one catalog (astropy table) object containing
	-- or linking to -- all the required data.

        In other words, this is a function that you could pass to meas.run.general() etc.

        If you want to combine several shape measurement algorithms into one shot, you would
	define such a function yourself (not here in megalut, but somewhere in your scripts).
        The present measfct serves as an example and is a bit long. It could be kept very short.

        :param catalog: an astropy table, which, in this case, is expected to have
	                catalog.meta["img"] set to be a megalut.tools.imageinfo.ImageInfo object.
        :param kwargs: keyword arguments that will be passed to the lower-level measure() function.
                       These set parameters of the shape measurement, but they do not pass any data.
		       Do not try to specify "img" or "xname" here, it will fail! Set the catalog's
		       meta["img"] instead.
                       So for this particular measfct, you probably want to give at least stampsize
		       as kwarg.
        """

	# check for stampsize for "img"
	stampsize = catalog.meta[runon].get_stampsize(stampsize)

	# load the images:
	img = catalog.meta[runon].load()

        # And we pass it, with all required kwargs, to the lower-level function:
	return measure(img, catalog,
		       xname=catalog.meta[runon].xname, yname=catalog.meta[runon].yname,
		       stampsize=stampsize,
		       **kwargs)


def measure(img, catalog, stampsize=None, xname="x", yname="y", prefix="fdnt_",
	    sewpy_workdir='sewpy', psfxname="psfx", psfyname="psfy", psfstampsize=128,):
	"""
	Use the pixel positions provided via the input table to measure their shape parameters.
	Return a copy of the given catalog, with new columns appended.
	
	:param img: image to be measured
	:param catalog: astropy table of objects to be measured
	:param psfimg: PSF image that is convolved into the image

	:param stampsize: img stamp size
	:param xname: column name containing the x coordinates in pixels
	:param yname: column name containing the y coordinates in pixels
	:param prefix: a string to prefix the field names that are added to the catalog
	:param sewpy_workdir: workdir for SExtractor run
	:param psfxname: column name containing the x coordinates of the PSF in pixels
	:param psfyname: column name containing the y coordinates of the PSF in pixels
	:param stampsize: psfimg stamp size
	
	:returns: astropy table (the original catalog, with additional columns of measurement values)
	
	"""
	
	starttime = datetime.now()
	
	# Check that the required SExtractor info is in catalog
	params = ["AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
		  "FLAGS_WIN", "FWHM_IMAGE", "BACKGROUND", "FLAGS", "psf_FLUX_RADIUS"]
	for param in params:
		if param not in catalog.colnames:
			print 'fdntfunc.py: input catalog missing SExtractor measurement info (%s); exiting' % param
			sys.exit(1)

	# OPEN ALL NECESSARY FILES
	if type(img) is str:

		logger.debug("Filepath given, loading the corresponding image...")
		img = tools.image.loadimg(img)
		img.setOrigin(0,0)     # for it to work with megalut.tools.image.getstamp()

	if type(psfimg) is str:

		psf_img = tools.image.loadimg(psfimg)
		psf_img.setOrigin(0,0)  # for it to work with megalut.tools.image.getstamp()

	# Prepare an output table with all the required columns
	output = astropy.table.Table(copy.deepcopy(catalog))  #, masked=True) # Convert the table to a masked table
	output.add_columns([

		astropy.table.Column(name=prefix+"flag", data=np.zeros(len(output), dtype=int)),
		astropy.table.Column(name=prefix+"flux", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"x", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"y", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"g1", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"g2", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"sigma", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"b22", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"snratio", dtype=float, length=len(output)),

		astropy.table.Column(name=prefix+"psf_flags", data=np.zeros(len(output), dtype=int)),
		astropy.table.Column(name=prefix+"psf_g1", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_g2", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_sigma", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_order", data=np.zeros(len(output), dtype=int)),
		astropy.table.Column(name=prefix+"psf_b00", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_b00_var", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_b22", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_chisq", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"psf_DOF", data=np.zeros(len(output), dtype=int)),
	])
	# By default, all these entries are masked:
	for col, col_fill in zip(["flux", "x", "y", "g1", "g2", "sigma", "b22", "snratio",
				  "psf_flags", "psf_g1", "psf_g2", "psf_sigma", "psf_b22", "flag",
				  "psf_order", "psf_b00", "psf_b00_var", "psf_chisq", "psf_DOF"],
				 [   -1.,  0.,  0., -10., -10.,     -1.,    -1.,        0.,
				            0,     -10.,     -10.,         -1.,        -1.,    -1,
				           -1,        0.,             0.,         0.,        0]):
		output[prefix+col][:] = col_fill

	# Similarly, we prepare columns for the sky stats:
	output.add_columns([
			astropy.table.Column(name="skystd", dtype=float, length=len(output)),
			astropy.table.Column(name="skymad", dtype=float, length=len(output)),
			astropy.table.Column(name="skymean", dtype=float, length=len(output)),
			astropy.table.Column(name="skymed", dtype=float, length=len(output))
			])

	# Save something useful to the meta dict
	output.meta[prefix + "xname"] = xname
	output.meta[prefix + "yname"] = yname
	
	n = len(output)
	
	# Loop over each object

	# DEBUG BLOCK
	count = 0
	mincount, maxcount = (4, 13)

	for obj in output:
		
		# DEBUG BLOCK
		count += 1  ## DEBUG
		if count < mincount: continue  ## DEBUG
		# Some simplistic progress indication:
		if obj.index%5000 == 0:  # is "index" an astropy table entry?
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(obj.index)/float(n),
							       obj.index, n))

		# get centroid, size and shear estimates from catalog
		(x, y) = (obj[xname], obj[yname])  # otherwise it may spill over the edge...
		(psfx, psfy) = (obj[psfxname], obj[psfyname])
		(a,b,theta) = (obj['AWIN_IMAGE'], obj['BWIN_IMAGE'], obj['THETAWIN_IMAGE'])
		size = np.hypot(a,b)  # in pixels
		psf_size = obj['psf_FLUX_RADIUS']   # psf_FLUX_RADIUS == psfEE50

		# TODO: figure out why some objects are not detected by SExtractor
		if obj['assoc_flag'] == False:   # not detected by SExtractor
			print 'SExtractor failed on this object'
			continue

		# get the PSF postage stamp image
		# according to megalut.sim.stampgrid, the xy coords are the same as that of galaxies
		(psfstamp, flag) = tools.image.getstamp(psfx, psfy, psf_img, psfstampsize)
		psfstamp = psfstamp.copy()   # if I want to move the pixel coords, then I need a copy for RunFDNT() to work
		if flag != 0:   # postage stamp extraction unsuccessful
			print 'psfstamp extraction failure'
			continue

		# get the galaxy postage stamp image (so much faster!)
		(galstamp, flag) = tools.image.getstamp(x, y, img, stampsize)
		galstamp = galstamp.copy()
		if flag != 0:   # postage stamp extraction unsuccessful
			print 'galstamp extraction failure'
			continue

		# find the noise level around the stamp
		sky_out = utils.skystats(galstamp)
		obj["skystd"] = sky_out["std"]
		obj["skymad"] = sky_out["mad"]  # median absolute deviation scaled to std
		obj["skymean"] = sky_out["mean"]
		obj["skymed"] = sky_out["med"]

		# add padding, 2x the stamp size, for FFT purposes
		safe_pad_margin = 4
		noise_pad_size = max(galstamp.array.shape) * 2.0 + safe_pad_margin
		noise_pad_image = galsim.Image(noise_pad_size, noise_pad_size, dtype=galstamp.dtype)
		rng = galsim.BaseDeviate()
		noise = galsim.GaussianNoise(rng, sigma=sky_out["mad"])  # mad is more robust than std
		noise_pad_image.addNoise(noise)
		noise_pad_image += sky_out["med"]  # median is more robust than mean
		galstamp = galstamp.view()
		galstamp_center = galstamp.center()
		galstamp.setCenter(0,0)
		noise_pad_image.setCenter(0,0)
		if noise_pad_image.bounds.includes(galstamp.bounds):
			noise_pad_image[galstamp.bounds] = galstamp   # now the center has galaxy image
		else:
			noise_pad_image = galstamp
		galstamp = noise_pad_image
		galstamp.setCenter(galstamp_center)

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
			logger.debug("GLMoments failed with %s:\n %s" % (m, str(obj)), exc_info=True)
			#print "GLMoments failed on:\n %s" % (str(gal))
			obj[prefix + "flag"] = -1
			if count >= maxcount:  break   ## DEBUG
			continue

		obj[prefix + "flag"] = res.intrinsic_flags

		try:
			# first PSF measurement info
			obj[prefix+'psf_flags'] = res.psf_flags
			obj[prefix+'psf_g1'] = res.psf_e1
			obj[prefix+'psf_g2'] = res.psf_e2
			obj[prefix+'psf_sigma'] = res.psf_sigma
			obj[prefix+'psf_b22'] = res.psf_b22
			obj[prefix+'psf_b00'] = res.psf_b00
			obj[prefix+'psf_b00_var'] = res.psf_b00_var
			obj[prefix+'psf_order'] = res.psf_order
			obj[prefix+'psf_chisq'] = res.psf_chisq
			obj[prefix+'psf_DOF'] = res.psf_DOF
			# native (galaxy + psf) measurement info
			# intrinsic galaxy info
			s = galsim.Shear(e1=res.intrinsic_e1, e2=res.intrinsic_e2)
			g1 = s.getG1()
			g2 = s.getG2()
			obj[prefix+"g1"] = g1
			obj[prefix+"g2"] = g2
			obj[prefix+"flux"] = res.observed_b00
			obj[prefix+"x"] = res.observed_centroid.x
			obj[prefix+"y"] = res.observed_centroid.y
			obj[prefix+"sigma"] = res.intrinsic_sigma
			# note: b_22 = rho4-4*rho2+2 = rho4-4*b_11+2*b_00;  b22 is a substitute
			#obj[prefix+"b22"] = res.intrinsic_b22
			obj[prefix + "snratio"] = res.observed_significance

		except ValueError:
			print "results not set correctly"  # NOTE: currently no masking is applied
			pass  # do nothing, this will "mask" the value out from the astropy table.

		## DEBUG BLOCK
		if count >= maxcount:
			print output[:maxcount]
			print output[:maxcount][prefix+'g1', prefix+'g2', prefix+'flux', prefix+'x', prefix+'y',
					 prefix+'sigma', prefix+'flag', prefix+'snratio',
					 #prefix+'psf_g1', prefix+'psf_g2', prefix+'psf_flags',
				         #prefix+'psf_sigma', prefix+'psf_order'
					 ]
			return output

	endtime = datetime.now()	
	logger.info("All done")

	nfailed = np.sum(output[prefix+"flag"] >= 8)
	
	logger.info("GLMoment() failed on %i out of %i sources (%.1f percent)" % \
			    (nfailed, n, 100.0*float(nfailed)/float(n)))
	logger.info("This measurement took %.3f ms per galaxy" % \
			    (1e3*(endtime - starttime).total_seconds() / float(n)))
	
	print output  ## DEBUG
	return output



	
	

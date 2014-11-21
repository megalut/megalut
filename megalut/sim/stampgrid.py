"""
Functions to draw grids of simulated galaxies into FITS images.
"""

import numpy as np
import math
import random
import os
import sys

import logging
logger = logging.getLogger(__name__)

import astropy.table
import galsim
from datetime import datetime

from .. import tools


def drawcat(params, n=10, stampsize=64, idprefix=""):
	"""
	Generates a catalog of all the "truth" input parameters for each simulated galaxy.
	
	:param params: a sim.Params instance that defines the distributions of parameters
	:param n: sqrt(number): I will generate n x n galaxies, on a grid !
	:type n: int	
	:param stampsize: width = height of desired stamps, in pixels
	:type stampsize: int
	:param idprefix: a string to use as prefix for the galaxy ids. Was tempted to call this idefix.
	
	:returns: A catalog (astropy table). The stampsize is stored in meta.
	
	"""
	if int(stampsize)%2 != 0:
		raise RuntimeError("stampsize should be even!")

	logger.info("Drawing a catalog of %i x %i galaxies..." % (n, n))
		
	# This explicit loop is kept for the sake of clarity.
	rows = []
	for iy in range(n):
		for ix in range(n):
		
			gal = params.get(ix, iy, n) # "gal" is a dict, whose values contain parameters for the galaxy
			gal["ix"] = ix
			gal["iy"] = iy
			gal["id"] = idprefix + str(ix + n*iy)
			gal["x"] = ix*stampsize + stampsize/2.0 + 0.5 # I'm not calling this tru_x, as it will be jittered, and also as a simple x is default.
			gal["y"] = iy*stampsize + stampsize/2.0 + 0.5
			rows.append(gal) # So rows will be a list of dicts
		
	# There are many ways to build a new astropy.table
	# One of them directly uses a list of dicts...
	
	catalog = astropy.table.Table(rows=rows)
	logger.info("Drawing of catalog done")
	
	catalog.meta["n"] = n
	catalog.meta["stampsize"] = stampsize
	
	
	return catalog
	



def drawimg(catalog, psfimg = None, psfxname="psfx", psfyname="psfy",
			simgalimgfilepath = "test.fits", simtrugalimgfilepath = None, simpsfimgfilepath = None):

	"""
	Turns a catalog as obtained from drawcat into FITS images.
	Only the position jitter and the pixel noise are randomized. All the other info is taken from the input catalogs.
	So simply call me several times for the same input to get different realizations of the same galaxies.
	To specify the PSF, pass me a psfimg, and add the columns given by psfxname and psfyname to the catalog.
	
	:param catalog: an input catalog of galaxy shape parameters, as returned by drawcat.
		The corresponding stampsize must be provided as catalog.meta["stampsize"].
		If you specify a psfimg, you'll also have to add the PSF coordinates for each galaxy to this catalog.
		The stampsize of the PSFs must be provided as catalog.meta["psfstampsize"].
	:param psfimg: filepath to a FITS image containing the PSFs to be used, or directly the GalSim image.
		Depending on the size of this image, one or the other option might be better. If you use run.multi(),
		ncat * nrea copies of this parameter will be made, and so better pass a filepath if the image is large.
	:type psfimg: GalSim image or string
	:param psfxname: column name of catalog containing the PSF x coordinate in pixels (not the index)
	:param psfyname: idem for y
	:param simgalimgfilepath: where I write my output image
	:param simtrugalimgfilepath: (optional) where I write the image without convolution and noise
	:param simpsfimgfilepath: (optional) where I write the PSFs
	
	.. note::
		See this function in MegaLUT v4 (great3) for attemps to speed up galsim by playing with fft params, accuracy, etc...
	
	.. note::
		About speed, if you specify trunc, better express the scale radius.
		But scale radius is crazy dependent on n, so I keep half-light-radius
		http://galsim-developers.github.io/GalSim/classgalsim_1_1base_1_1_sersic.html
	
	"""
	starttime = datetime.now()	
	
	if "n" not in catalog.meta.keys():
		raise RuntimeError("Provide n in the meta data of the input catalog to drawimg.")
	if "stampsize" not in catalog.meta.keys():
		raise RuntimeError("Provide stampsize in the meta data of the input catalog to drawimg.")	
	
	n = catalog.meta["n"]
	stampsize = catalog.meta["stampsize"] # The stamps I'm going to draw
		
	logger.info("Drawing images of %i galaxies on a %i x %i grid..." % (len(catalog), n, n))
	logger.info("The stampsize for the simulated galaxies is %i." % (stampsize))
	
	if psfimg is not None: # If the user provided some PSFs:

		if "psfstampsize" not in catalog.meta.keys():
			raise RuntimeError("Given that you specified a psfimg, provide psfstampsize in the meta data of the input catalog to drawimg.")	
		psfstampsize = catalog.meta["psfstampsize"] # Size of the PSF stamps that I should extract from psfimg
		logger.info("I will use provided PSFs with a stampsize of %i." % (psfstampsize))
		if not(psfxname in catalog.colnames and psfyname in catalog.colnames):
			raise RuntimeError("psfxname (%s) and psfyname (%s) are not available in the catalog" % (psfxname,psfyname))

		if type(psfimg) is str:
			logger.debug("You gave me a filepath, and I'm now loading the image...")
			psfimg = tools.image.loadimg(psfimg)
				
	else:
		logger.info("No PSFs given: I will use plain Gaussians!")

	
	# Galsim random number generators
	rng = galsim.BaseDeviate()
	ud = galsim.UniformDeviate() # This gives a random float in [0, 1)

	# We prepare the big images :
	gal_image = galsim.ImageF(stampsize * n , stampsize * n)
	trugal_image = galsim.ImageF(stampsize * n , stampsize * n)
	psf_image = galsim.ImageF(stampsize * n , stampsize * n)

	gal_image.scale = 1.0
	trugal_image.scale = 1.0
	psf_image.scale = 1.0

	# And loop through the catalog:
	for row in catalog:
		
		# Some simplistic progress indication:
		fracdone = float(row.index) / len(catalog)
		if row.index%500 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (fracdone*100.0, row.index, len(catalog)))
		
		# We will draw this galaxy in a postage stamp, but first we need the bounds of this stamp.
		ix = int(row["ix"])
		iy = int(row["iy"])
		assert ix < n and iy < n
		bounds = galsim.BoundsI(ix*stampsize+1 , (ix+1)*stampsize, iy*stampsize+1 , (iy+1)*stampsize) # Default Galsim convention, index starts at 1.
		gal_stamp = gal_image[bounds]
		trugal_stamp = trugal_image[bounds]
		psf_stamp = psf_image[bounds]
	
		# We draw a sersic profile
		gal = galsim.Sersic(n=row["tru_sersicn"], half_light_radius=row["tru_rad"], flux=row["tru_flux"])
		gal.applyShear(g1=row["tru_g1"], g2=row["tru_g2"]) # This combines shear AND the ellipticity of the galaxy
		
		# We apply some jitter to the position of this galaxy
		xjitter = ud() - 0.5 # This is the minimum amount -- should we do more, as real galaxies are not that well centered in their stamps ?
		yjitter = ud() - 0.5
		gal.applyShift(xjitter,yjitter)
		
		# We draw the pure unconvolved galaxy
		gal.draw(trugal_stamp)

		# We get the PSF stamp, if provided
		if psfimg is not None:
			(inputpsfstamp, flag) = tools.image.getstamp(row[psfxname], row[psfyname], psfimg, psfstampsize)
			if flag != 0:
				raise RuntimeError("Could not extract a %ix%i stamp at (%.2f, %.2f) from the psfimg" % (psfstampsize, psfstampsize, row[psfxname], row[psfyname]))
			psf = galsim.InterpolatedImage(inputpsfstamp, flux=1.0, dx=1.0)
			psf.draw(psf_stamp) # psf_stamp has a different size than inputpsfstamp, so this could lead to problems one day.
					
		else:
			#psf = galsim.OpticalPSF(lam_over_diam = 0.39, defocus = 0.5, obscuration = 0.1)# Boy is this slow, do not regenerate for every stamp !
			psf = galsim.Gaussian(flux=1., sigma=1.5)
			psf.draw(psf_stamp)

		# Convolution by the PSF
		galconv = galsim.Convolve([gal,psf], real_space=False)
		
		# Draw the convolved galaxy	
		galconv.draw(gal_stamp)
		
		# And add shot noise to the convolved galaxy:
		gal_stamp.addNoise(galsim.GaussianNoise(rng, sigma=row["tru_sig"]))
		
		
	logger.info("Done with drawing, now writing output FITS files ...")	

	gal_image.write(simgalimgfilepath)
	
	if simtrugalimgfilepath != None:
		trugal_image.write(simtrugalimgfilepath)
	
	if simpsfimgfilepath != None:
		psf_image.write(simpsfimgfilepath)
	
	endtime = datetime.now()
	logger.info("This drawing took %s" % (str(endtime - starttime)))




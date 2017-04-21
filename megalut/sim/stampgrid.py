"""
Functions to draw grids of simulated galaxies into FITS images.
"""

import numpy as np
import math
import random
import os
import sys
import copy

import logging
logger = logging.getLogger(__name__)

import astropy.table
import galsim
from datetime import datetime

from .. import tools
from . import params


def drawcat(simparams, n=10, nc=2, stampsize=64, idprefix=""):
	"""
	Generates a catalog of all the "truth" input parameters for each simulated galaxy.
	
	:param simparams: a sim.Params instance that defines the distributions of parameters
	:param n: number of galaxies (must be a multiple of nc)
		
	:type n: int
	:param nc: number of "columns" on which I should place these galaxies
		Note that the effective number of "columns" (called nx in the code) might get inflated if you use shape noise cancelation!
	:type nc: int
	:param stampsize: width = height of desired stamps, in pixels
	:type stampsize: int
	:param idprefix: a string to use as prefix for the galaxy ids. Was tempted to call this idefix.
	
	The ix index moves faster than the iy index when iterating over the output catalog.
	So if you want a parameter to change seldomly, link it to the iy index.
	Different SNC-versions of a galaxy are placed directly one after the other, with consecutive ix indices but same iy.
	(however for the purpose of drawing the parameters, the SNC-versions *all* have the same ix as well, of course)
	
	:returns: A catalog (astropy table). The stampsize is stored in meta.
	
	"""
	if int(stampsize)%2 != 0:
		raise RuntimeError("stampsize should be even!")

	if n % nc != 0 or n < nc:
		raise RuntimeError("n must be a multiple of nc!")

	logger.info("Drawing a catalog of %i truly different galaxies using params '%s'..." % (n, simparams))
	statparams = simparams.stat() # We call this only *once*
	logger.info("The params '{simparams.name}' have stat '{0}'".format(statparams, simparams=simparams))
	
	ny = int(int(n)/int(nc)) # number of lines does not change with SNC.
	if statparams["snc_type"] == 0:	
		nsnc = 1 # the number of SNC versions. "No SNC" means the same thing as "1 SNC"...
	elif statparams["snc_type"] > 0:
		nsnc = statparams["snc_type"] # If snc_type is positive, it simply corresponds to the number of SNC rotations!
	else:
		raise RuntimeError("Did not understand snc_type")
	nx = nsnc * nc
	sncrot = 180.0/float(nsnc) # Rotation for SNC, in degrees. For example, 90.0 for snc_type == 2
	
	logger.info("The grid will be %i x %i, and the number of SNC rotations is %i." % (nx, ny, nsnc))
	
	rows = [] # The "table"
	for i in range(n): # We loop over all "truely different" galaxies (not all SNC galaxies)
		
		# The indices used to draw parameters for each of these truely different galaxies:
		(piy, pix) = divmod(i, nc)		
		assert pix < nc and piy < ny
	
		# And draw one:
		gal = simparams.draw(pix, piy, nc, ny)
		
		# Now things get different depending on SNC
		if statparams["snc_type"] == 0:	# No SNC, so we simply add this galaxy to the list.
		
			gal["ix"] = pix
			gal["iy"] = piy
			
			gal.update(statparams) # This would overwrite any of the "draw" params.
			rows.append(gal) # So rows will be a list of dicts
		
		
		else: # SNC with nsnc different versions rotated by sncrot degrees
		
			for roti in range(nsnc):
				rotgal = copy.deepcopy(gal)
				
				# We perform the rotation in different ways, depending on the parametrisation
				profile_type = params.profile_types[rotgal["tru_type"]]
				if profile_type in ["Sersic", "Gaussian"]:
					(rotgal["tru_g1"], rotgal["tru_g2"]) = tools.calc.rotg(gal["tru_g1"], gal["tru_g2"], roti*sncrot)
				elif profile_type is "EBulgeDisk":
					rotgal["tru_theta"] = gal["tru_theta"] + roti*sncrot
				else:
					raise RuntimeError("Unknown profile type")
				
				# And now each of the SNC versions gets a consecutive ix but the same iy:
				rotgal["ix"] = pix * nsnc + roti
				rotgal["iy"] = piy
				
				rotgal.update(statparams)
				rows.append(rotgal)
				#print rotgal
		
		
	# A second loop simply adds the pixel positions and ids, for all galaxies (not just truely different ones):
	for (i, gal) in enumerate(rows):
		gal["id"] = idprefix + str(i)
		gal["x"] = gal["ix"]*stampsize + stampsize/2.0 + 0.5 # I'm not calling this tru_x, as it will be jittered, and also as a simple x is default.
		gal["y"] = gal["iy"]*stampsize + stampsize/2.0 + 0.5
			
				
	# There are many ways to build a new astropy.table
	# One of them directly uses a list of dicts...
	
	catalog = astropy.table.Table(rows=rows)
	logger.info("Drawing of catalog done")
	
	# The following is aimed at drawimg:
	catalog.meta["stampsize"] = stampsize
	
	# Checking the catalog length
	assert len(catalog) == nsnc * n
	
	# Adding some useful stuff to the meta:
	catalog.meta["nx"] = nx
	catalog.meta["ny"] = ny
	catalog.meta["nsnc"] = nsnc
	catalog.meta["snc_type"] = statparams["snc_type"]
	
	return catalog
	



def drawimg(catalog, simgalimgfilepath="test.fits", simtrugalimgfilepath=None, simpsfimgfilepath=None):

	"""
	Turns a catalog as obtained from drawcat into FITS images.
	Only the position jitter and the pixel noise are randomized. All the other info is taken from the input catalog.
	So simply call me several times for the same input to get different realizations of the same galaxies.
	To specify the PSFs, add a meta["psf"] ImageInfo object to the catalog.
		
	:param catalog: an input catalog of galaxy shape parameters, as returned by drawcat.
		The corresponding stampsize must be provided as catalog.meta["stampsize"].
		If you specify a psf image in catalog.meta["psf"], your catalog must of course also contain
		PSF coordinates for that image.
		If no PSF stamps are specifed, the code will look for Gaussian PSF parameters in the catalog.
		If such parameters are not given, no PSF convolution is done.
		
	:param simgalimgfilepath: where I write my output image of simulated and noisy galaxies
	:param simtrugalimgfilepath: (optional) where I write the image without convolution and noise
	:param simpsfimgfilepath: (optional) where I write the PSFs
	
	.. note::
		See this function in MegaLUT v4 (great3) for attempts to speed up galsim by playing with fft params, accuracy, etc...
	
	.. note::
		About speed, if you specify trunc, better express the scale radius.
		But scale radius is crazy dependent on n, so I keep half-light-radius
		http://galsim-developers.github.io/GalSim/classgalsim_1_1base_1_1_sersic.html
	
	"""
	starttime = datetime.now()	
	
	gsparams = galsim.GSParams(maximum_fft_size=8192)
	
	if "nx" not in catalog.meta.keys() or "ny" not in catalog.meta.keys():
		raise RuntimeError("Provide nx and ny in the meta data of the input catalog to drawimg.")
	if "stampsize" not in catalog.meta.keys():
		raise RuntimeError("Provide stampsize in the meta data of the input catalog to drawimg.")	
	
	nx = catalog.meta["nx"]
	ny = catalog.meta["ny"]
	stampsize = catalog.meta["stampsize"] # The stamps I'm going to draw
		
	logger.info("Drawing images of %i galaxies on a %i x %i grid..." % (len(catalog), nx, ny))
	logger.info("The stampsize for the simulated galaxies is %i." % (stampsize))

	# A special function checks the combination of settings in the provided catalog:
	todo = checkcat(catalog)
	
	if "loadpsfimg" in todo:
		psfimg = catalog.meta["psf"].load() # Loading the actual GalSim Image
		psfinfo = catalog.meta["psf"]

	if "tru_pixel" in todo:
		# This is only if you want "effective pixels" larger than the actual pixels (related to SBE, normally you don't want this).
		pix = galsim.Pixel(catalog["tru_pixel"][0]) # We have checked in checkcat that all values are equal.
		
	# Galsim random number generators
	rng = galsim.BaseDeviate()
	ud = galsim.UniformDeviate() # This gives a random float in [0, 1)

	# We prepare the big images :
	gal_image = galsim.ImageF(stampsize * nx , stampsize * ny)
	trugal_image = galsim.ImageF(stampsize * nx , stampsize * ny)
	psf_image = galsim.ImageF(stampsize * nx , stampsize * ny)

	gal_image.scale = 1.0 # These pixel scales make things easier. If you change them, be careful to also adapt the jitter scale!
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
		assert ix < nx and iy < ny
		bounds = galsim.BoundsI(ix*stampsize+1 , (ix+1)*stampsize, iy*stampsize+1 , (iy+1)*stampsize) # Default Galsim convention, index starts at 1.
		gal_stamp = gal_image[bounds]
		trugal_stamp = trugal_image[bounds]
		psf_stamp = psf_image[bounds]
	
		# We draw the desired profile
		profile_type = params.profile_types[row["tru_type"]]
		
		if profile_type == "Sersic":
			
			gal = galsim.Sersic(n=float(row["tru_sersicn"]), half_light_radius=float(row["tru_rad"]), flux=float(row["tru_flux"]), gsparams=gsparams)
			# We make this profile elliptical
			gal = gal.shear(g1=row["tru_g1"], g2=row["tru_g2"]) # This adds the ellipticity to the galaxy

		elif profile_type == "Gaussian":
			
			gal = galsim.Gaussian(flux=float(row["tru_flux"]), sigma=float(row["tru_sigma"]), gsparams=gsparams)
			# We make this profile elliptical
			gal = gal.shear(g1=row["tru_g1"], g2=row["tru_g2"]) # This adds the ellipticity to the galaxy

		elif profile_type == "EBulgeDisk":
			
			# A slightly more advancec Bulge + Disk model
			# It needs GalSim version master, as of April 2017 (probably 1.5).
			
			# Get a Sersic=4 bulge:
			bulge = galsim.Sersic(n=4.0, half_light_radius=row["tru_bulge_hlr"], flux=row["tru_bulge_flux"])
			# Make it elliptical:
			bulge_ell = galsim.Shear(g=row["tru_bulge_g"], beta=row["tru_theta"] * galsim.degrees)
			bulge = bulge.shear(bulge_ell)
			
			# Get a disk
			scale_radius = row["tru_disk_hlr"] / galsim.Exponential._hlr_factor
			disk = galsim.InclinedExponential(inclination=row["tru_disk_tilt"] * galsim.degrees, scale_radius=scale_radius,
				flux=row["tru_disk_flux"], scale_h_over_r=row["tru_disk_scale_h_over_r"])
			# Rotate it in the same orientation as the bulge:
			disk = disk.rotate(row["tru_theta"] * galsim.degrees)
			
			# And we add those profiles, as done in GalSim demo3.py :
			gal = bulge + disk
			
		else:
			raise RuntimeError("Unknown galaxy profile!")	
		
		
		# And now we add lensing, if s1, s2 and mu are different from no lensing...
		if row["tru_s1"] != 0 or row["tru_s2"] != 0 or row["tru_mu"] != 1:
			gal = gal.lens(float(row["tru_s1"]), float(row["tru_s2"]), float(row["tru_mu"]))
		else:
			pass
			#logger.info("No lensing!")
		
		
		# We apply some jitter to the position of this galaxy
		xjitter = ud() - 0.5 # This is the minimum amount -- should we do more, as real galaxies are not that well centered in their stamps ?
		yjitter = ud() - 0.5
		gal = gal.shift(xjitter,yjitter)
		
		# We draw the pure unconvolved galaxy
		if simtrugalimgfilepath != None:
			gal.drawImage(trugal_stamp, method="auto") # Will convolve by the sampling pixel.

		# We prepare/get the PSF and do the convolution:
		
		# Should the final operation skip the convolution by the pixel (because the PSF already is in large pixels) ?
		skip_pixel_conv = False
		
		if "usegausspsf" in todo:
			
			psf = galsim.Gaussian(flux=1., sigma=row["tru_psf_sigma"])
			
			psf = psf.shear(g1=row["tru_psf_g1"], g2=row["tru_psf_g2"])
			# Let's apply some jitter to the position of the PSF (not sure if this is required, but should not harm ?)
			psf_xjitter = ud() - 0.5
			psf_yjitter = ud() - 0.5
			psf = psf.shift(psf_xjitter,psf_yjitter)
			if simpsfimgfilepath != None:
				psf.drawImage(psf_stamp, method="auto") # Will convolve by the sampling pixel.
	
			if "tru_pixel" in todo: # Not sure if this should only apply to gaussian PSFs, but so far this seems OK.
				# Remember that this is an "additional" pixel convolution, not the usual sampling-related convolution that happens in drawImage.
				galconv = galsim.Convolve([gal, psf, pix])
			
			else:
				galconv = galsim.Convolve([gal,psf])
			
		elif "loadpsfimg" in todo:
			
			(inputpsfstamp, flag) = tools.image.getstamp(row[psfinfo.xname], row[psfinfo.yname], psfimg, psfinfo.stampsize)
			psfpixelscale = getattr(psfinfo, "pixelscale", 1.0) # Using getattr so that it works with old objects as well
			if psfpixelscale > 0.5:
				#logger.warning("You seem to be using a sampled PSF with large pixels (e.g., observed stars). I'll do my best and skip the pixel conv, but this might well lead to errors.")
				skip_pixel_conv = True
			if flag != 0:
				raise RuntimeError("Could not extract a %ix%i stamp at (%.2f, %.2f) from the psfimg %s" %\
					(psfinfo.stampsize, psfinfo.stampsize, row[psfinfo.xname], row[psfinfo.yname], psfinfo.name))
			psf = galsim.InterpolatedImage(inputpsfstamp, flux=1.0, scale=psfpixelscale)
			if simpsfimgfilepath != None:
				psf.drawImage(psf_stamp, method="no_pixel") # psf_stamp has a different size than inputpsfstamp, so this could lead to problems one day.
			
			#galconv = galsim.Convolve([gal,psf], real_space=False)	
			galconv = galsim.Convolve([gal,psf])	

		elif "nopsf" in todo:
			# Nothing to do		
			galconv = gal
			
		else:
			raise RuntimeError("Bug in todo.")
	
		# Draw the convolved galaxy	
		if skip_pixel_conv == False:	
			galconv.drawImage(gal_stamp, method="auto") # This will convolve by the image sampling pixel. Don't do this yourself ahead! 
		else:
			#logger.warning("NOT computing any pixel convolution")
			galconv.drawImage(gal_stamp, method="no_pixel") # Simply uses pixel-center values. Know what you are doing, see doc of galsim. 

		
		# And add noise to the convolved galaxy:
		gal_stamp.addNoise(galsim.CCDNoise(rng, sky_level=float(row["tru_sky_level"]), gain=float(row["tru_gain"]), read_noise=float(row["tru_read_noise"])))
	
		
	logger.info("Done with drawing, now writing output FITS files ...")	

	gal_image.write(simgalimgfilepath)
	
	if simtrugalimgfilepath != None:
		trugal_image.write(simtrugalimgfilepath)
	
	if simpsfimgfilepath != None:
		psf_image.write(simpsfimgfilepath)
	
	endtime = datetime.now()
	logger.info("This drawing took %s" % (str(endtime - starttime)))



def checkcat(cat):
	"""
	Checks the input catalog for consistency, compliance, and purpose (-> "to do"...)
	This function is mainly here to make things fail nicely if something is missing.
	It returns a list containing flags that will control some aspects of drawimg.
	"""
	
	todo = [] # The output list.
	
	# We check some fields that should always be there:
	for f in ["tru_type", "tru_sky_level", "tru_gain", "tru_read_noise"]:
		if f not in cat.colnames:
			raise RuntimeError("The field '%s' is not in the catalog (i.e., the simulation parameters)!" % (f))

	# What profiles do we have in there ?
	contained_profile_types = list(set([params.profile_types[row["tru_type"]] for row in cat]))
	logger.info("Galaxy profile types to be simulated: %s" % (str(contained_profile_types)))	

	# We check the additional required fields for each of these profile types
	if "Gaussian" in contained_profile_types:
		for f in ["tru_sigma", "tru_g1", "tru_g2"]:
			if f not in cat.colnames:
				raise RuntimeError("I should draw a Gaussian profile, but '%s' is not in the catalog (i.e., the simulation parameters)!" % (f))
	if "Sersic" in contained_profile_types:
		for f in ["tru_rad", "tru_sersicn", "tru_g1", "tru_g2"]:
			if f not in cat.colnames:
				raise RuntimeError("I should draw a Sersic profile, but '%s' is not in the catalog (i.e., the simulation parameters)!" % (f))
	if "EBulgeDisk" in contained_profile_types:
		for f in []:
			if f not in cat.colnames:
				raise RuntimeError("I should draw a Sersic profile, but '%s' is not in the catalog (i.e., the simulation parameters)!" % (f))

		
	# And now we check the information provided about the PSFs to be used
	
	if "psf" in cat.meta: # The user provided some PSFs in form of stamps
		logger.info("I will use provided PSF stamps (from '%s')" % (str(cat.meta["psf"])))
		cat.meta["psf"].checkcolumns(cat) # Check that the ImageInfo object matches to the catalog.
		
		todo.append("loadpsfimg")
				
	else: # I will look for PSF params in the catalog, and use analytical Gaussians
		
		psf_gauss_ok = True
		for f in ["tru_psf_sigma", "tru_psf_g1", "tru_psf_g2"]:
			if f not in cat.colnames:
				psf_gauss_ok = False
		
		if psf_gauss_ok:
			logger.info("I will use analytical Gaussians PSFs.")
			todo.append("usegausspsf")
		else:
			logger.warning("No or not enough PSF information given, I will NOT convolve the simulated galaxies!")
			todo.append("nopsf")
	
	
	# Now let's have a look at the extra pixel convolution (added with SBE in mind)
	
	if "tru_pixel" in cat.colnames:
		tru_pixels = list(set(cat["tru_pixel"]))
		if len(tru_pixels) != 1:
			raise RuntimeError("You're mixing seveal tru_pixel values, probably a mistake.") # If you ever change this, fix code that currently generates only one pix!
		tru_pixel = tru_pixels[0]
		if tru_pixel > 0.0:
			logger.warning("The galaxy profiles will be convolved with an extra {0:.1f} pixels".format(tru_pixel))
		
			todo.append("tru_pixel")
	
	return todo

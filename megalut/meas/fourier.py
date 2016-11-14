"""
Measurements on the FFT, maybe also "Fourier division"

"""

import numpy as np
import sys, os
import copy
from datetime import datetime

import scipy.signal

import logging
logger = logging.getLogger(__name__)

import astropy.table

import utils
import galsim_adamom
#import sewfunc # no need for sewpy
from .. import tools

#import galsim


def measfct(cat, runon="img", stampsize=None, prefix="fourier_", windowtype=None):
	"""
	
	"""
	
	# We get the stamp size to use:
	stampsize = cat.meta[runon].get_stampsize(stampsize)
	
	# We load the image:
	img = cat.meta[runon].load()

	xname = cat.meta[runon].xname
	yname = cat.meta[runon].yname
	
	# real images don't come in grids. So we have to define our own grid here, to save
	n = len(cat)
	ncols = 20
	nrows = int(np.ceil(float(n)/float(ncols)))
	
	#galimg = cat.meta["img"].load()
	#psfimg = cat.meta["psf"].load()
	#
	#galxname = cat.meta["img"].xname
	#galyname = cat.meta["img"].yname
	#
	#psfxname = cat.meta["psf"].xname
	#psfyname = cat.meta["psf"].yname
	#galstampsize = cat.meta["img"].stampsize
	#psfstampsize = cat.meta["psf"].stampsize
	
	#if galstampsize != psfstampsize:
	#	raise RuntimeError("Can't handle this for now")
	#stampsize = galstampsize
	
	
	workdir = cat.meta[runon].workdir
	if not os.path.exists(workdir):
		os.makedirs(workdir)
	
	logger.info("Will write FFTs into %s" % workdir)		
	logger.info("Will write to %i x %i stamps of %i x %i pixels" % (ncols, nrows, stampsize, stampsize))	
	

	cat = astropy.table.Table(copy.deepcopy(cat), masked=True) # Convert the table to a masked table
	# A bit stange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.
	
	cat.add_columns([
		astropy.table.Column(name=prefix+"x", dtype=float, length=len(cat)),
		astropy.table.Column(name=prefix+"y", dtype=float, length=len(cat))
	])
	
	
	# First attempt to use GalSim to construct the FFT stamp images:
	#fourier_image = galsim.ImageF(stampsize * ncols , stampsize * nrows)
	#fourier_image.setOrigin(0, 0)
	#test_image = galsim.ImageF(stampsize * ncols , stampsize * nrows)
	
	# For now let's use simply numpy arrays
	#fourier_gal_image = np.zeros((stampsize * ncols , stampsize * nrows), dtype=float)
	#fourier_psf_image = np.zeros((stampsize * ncols , stampsize * nrows), dtype=float)
	#fourier_gal_image_path = os.path.join(workdir, "fourier_gal.fits")
	#fourier_psf_image_path = os.path.join(workdir, "fourier_psf.fits")
	
	
	#real_image = np.zeros((stampsize * ncols , stampsize * nrows), dtype=float)
	#real_image_path = os.path.join(workdir, "real.fits")
	
	fft_image = np.zeros((stampsize * ncols , stampsize * nrows), dtype=float)
	fft_image_path = os.path.join(workdir, "fourier-{}.fits".format(prefix))
	
	
	# Preparing a window 
	if windowtype == None:
		pass
	elif windowtype == "Hann":
		logger.info("Preparing a Hann window...")
		window = np.outer(scipy.signal.hann(stampsize), np.ones(stampsize))
		window = np.sqrt(window * window.T)
	else:
		raise RuntimeError("Unknown window type")
	
	logger.info("Computing FFTs...")
	for gal in cat:

		"""
		# We get the galaxy and psf stamps:
		(galstamp, galflag) = tools.image.getstamp(row[galxname], row[galyname], galimg, stampsize)
		(psfstamp, psfflag) = tools.image.getstamp(row[psfxname], row[psfyname], psfimg, stampsize)
		
		gal = galstamp.array
		psf = psfstamp.array
		
		fgal = np.fft.fftshift(np.fft.fft2(gal))
		fpsf = np.fft.fftshift(np.fft.fft2(psf))
		"""
		# The deconvolution would require some masking
		"""
		fdec = fgal / fpsf
		dec = np.abs(np.fft.ifft2(np.fft.ifftshift(fdec)))
		"""
	
		#  Get stamp
		(stamp, flag) = tools.image.getstamp(gal[xname], gal[yname], img, stampsize)
		if flag != 0:
			raise RuntimeError("getstamp failed")
		stamp = stamp.array.transpose() # The transpose compensates for galsim internal convention 
	
		if windowtype != None:
			# Multiplying this with a smooth window to cancel effects of 
			stamp *= window
	
	
		# FFT, keeping only the norm:
		fftstamp = np.abs(np.fft.fftshift(np.fft.fft2(stamp)))
		
		# We subtract the background
		ss = utils.skystats(fftstamp)
		fftstamp -= ss["mean"]
		
		# Another option would be to estimate this level from the background mad measured in real space
		# (but careful with the window, then)
	
		# We write the result into the output stamp:
		ix = gal.index % ncols
		iy = gal.index // ncols
	
		#print ix, iy
		#bounds = galsim.BoundsI(ix*stampsize+1 , (ix+1)*stampsize, iy*stampsize+1 , (iy+1)*stampsize)
	
		xmin = ix*stampsize 
		xmax = (ix+1)*stampsize
		ymin = iy*stampsize
		ymax = (iy+1)*stampsize
		
		#print xmin, xmax, ymin, ymax
		#fourier_gal_image[xmin:xmax, ymin:ymax] = np.abs(fgal)
		#fourier_psf_image[xmin:xmax, ymin:ymax] = np.abs(fpsf)
		
		fft_image[xmin:xmax, ymin:ymax] = fftstamp
		#real_image[xmin:xmax, ymin:ymax] = stamp
		
		
		gal[prefix+"x"] = 1.0 + ((xmin + xmax) / 2.0) # The plus one is empirical, might be due to fftshift...
		gal[prefix+"y"] = 1.0 + ((ymin + ymax) / 2.0)
		
		#(fourierstamp, fourierflgalstampag) = tools.image.getstamp(x, y, fourier_image, stampsize)
		#fourierstamp = galstamp
		
	
	#tools.io.tofits(fourier_gal_image, fourier_gal_image_path)
	#tools.io.tofits(fourier_psf_image, fourier_psf_image_path)
	
	tools.io.tofits(fft_image, fft_image_path)
	#tools.io.tofits(real_image, real_image_path)
	
	
	# For now, we just call galsim_adamom on this stuff:
	cat = galsim_adamom.measure(
		fft_image_path,
		cat, xname=prefix+"x", yname=prefix+"y", stampsize=stampsize, prefix=prefix+"adamom_")
	
	# Now we tweak some fields to get features more similar to normal space
	
	cat[prefix+"adamom_g1"] *= -1.0		
	cat[prefix+"adamom_g2"] *= -1.0
	
	sigma_is_nice = np.logical_and(np.logical_not(cat[prefix+"adamom_sigma"].mask), cat[prefix+"adamom_sigma"] > 0.0)
			
	cat[prefix+"adamom_sigma"][sigma_is_nice] = 1.0 / cat[prefix+"adamom_sigma"][sigma_is_nice]
	
	
	"""
	cat = galsim_adamom.measure(
		real_image_path,
		cat, xname=prefix+"x", yname=prefix+"y", stampsize=stampsize, prefix=prefix+"real_adamom_")
	
	sewpy_config = {"DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
		"PHOT_FLUXFRAC":"0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9",
		"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
	
	sewpy_params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
		"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
		"FWHM_IMAGE", "KRON_RADIUS", "FLUX_RADIUS(7)", "BACKGROUND", "FLAGS"]
	
	cat = sewfunc.measure(fft_image_path, cat, xname=prefix+"x", yname=prefix+"y",
		config=sewpy_config,
		params=sewpy_params,
		workdir=workdir,
		sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex",
		prefix=prefix+"sewpy_"
		)
	"""
	
	return cat
	
	#fourier_image.write(os.path.join(workdir, "fourier.fits"))
	#test_image.write(os.path.join(workdir, "test.fits"))
		


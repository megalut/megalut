"""
Measurements on the FFT, maybe also "Fourier division"

"""

import numpy as np
import sys, os
import copy
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

import astropy.table

import utils
import galsim_adamom
from .. import tools

#import galsim


def measfct(cat, prefix="fourier_"):
	"""
	
	"""
	
	n = len(cat)
	ncols = 20
	nrows = int(np.ceil(float(n)/float(ncols)))
	
	galimg = cat.meta["img"].load()
	psfimg = cat.meta["psf"].load()
	
	galxname = cat.meta["img"].xname
	galyname = cat.meta["img"].yname
	psfxname = cat.meta["psf"].xname
	psfyname = cat.meta["psf"].yname
	
	galstampsize = cat.meta["img"].stampsize
	psfstampsize = cat.meta["psf"].stampsize
	
	if galstampsize != psfstampsize:
		raise RuntimeError("Can't handle this for now")
	stampsize = galstampsize
	
	
	workdir = cat.meta["img"].workdir
	if not os.path.exists(workdir):
		os.makedirs(workdir)
	
	logger.info("Will write FFTs into %s" % workdir)		
	logger.info("Will write to %i x %i stamps of %i x %i pixels" % (ncols, nrows, stampsize, stampsize))	
	

	output = astropy.table.Table(copy.deepcopy(cat), masked=True) # Convert the table to a masked table
	# A bit stange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.
	
	output.add_columns([
		astropy.table.Column(name=prefix+"x", dtype=float, length=len(output)),
		astropy.table.Column(name=prefix+"y", dtype=float, length=len(output))
	])
	
	
	# First attempt to use GalSim to construct the FFT stamp images:
	#fourier_image = galsim.ImageF(stampsize * ncols , stampsize * nrows)
	#fourier_image.setOrigin(0, 0)
	#test_image = galsim.ImageF(stampsize * ncols , stampsize * nrows)
	
	# For now let's use simply numpy arrays
	fourier_gal_image = np.zeros((stampsize * ncols , stampsize * nrows), dtype=float)
	fourier_psf_image = np.zeros((stampsize * ncols , stampsize * nrows), dtype=float)
	fourier_gal_image_path = os.path.join(workdir, "fourier_gal.fits")
	fourier_psf_image_path = os.path.join(workdir, "fourier_psf.fits")
	
	test_image = np.zeros((stampsize * ncols , stampsize * nrows), dtype=float)
	test_image_path = os.path.join(workdir, "fourier_test.fits")
	
	
	
	for row in output:

		# We get the galaxy and psf stamps:
		(galstamp, galflag) = tools.image.getstamp(row[galxname], row[galyname], galimg, stampsize)
		(psfstamp, psfflag) = tools.image.getstamp(row[psfxname], row[psfyname], psfimg, stampsize)
		
		gal = galstamp.array
		psf = psfstamp.array
		
		fgal = np.fft.fftshift(np.fft.fft2(gal))
		fpsf = np.fft.fftshift(np.fft.fft2(psf))
		
		# The deconvolution would require some masking
		"""
		fdec = fgal / fpsf
		dec = np.abs(np.fft.ifft2(np.fft.ifftshift(fdec)))
		"""
	
		# We write the result into the output stamp:
		ix = row.index % ncols
		iy = row.index // ncols
	
		#print ix, iy
		#bounds = galsim.BoundsI(ix*stampsize+1 , (ix+1)*stampsize, iy*stampsize+1 , (iy+1)*stampsize)
	
		xmin = ix*stampsize 
		xmax = (ix+1)*stampsize
		ymin = iy*stampsize
		ymax = (iy+1)*stampsize
		
		#print xmin, xmax, ymin, ymax
		fourier_gal_image[xmin:xmax, ymin:ymax] = np.abs(fgal)
		fourier_psf_image[xmin:xmax, ymin:ymax] = np.abs(fpsf)
		test_image[xmin:xmax, ymin:ymax] = gal
		
		
		row[prefix+"x"] = (xmin + xmax) / 2.0
		row[prefix+"y"] = (ymin + ymax) / 2.0
		
		#(fourierstamp, fourierflgalstampag) = tools.image.getstamp(x, y, fourier_image, stampsize)
		#fourierstamp = galstamp
		
	
	tools.io.tofits(fourier_gal_image, fourier_gal_image_path)
	tools.io.tofits(fourier_psf_image, fourier_psf_image_path)
	tools.io.tofits(test_image, test_image_path)
	
	# For now, we just call galsim_adamom on this stuff:
	output = galsim_adamom.measure(
		fourier_gal_image_path,
		output, xname=prefix+"x", yname=prefix+"y", stampsize=stampsize, measuresky=False, prefix=prefix+"adamom_")
	
	return output
	
	#fourier_image.write(os.path.join(workdir, "fourier.fits"))
	#test_image.write(os.path.join(workdir, "test.fits"))
		


"""
Functions to help visualizing postage stamps of selected sources in large images.
"""

from .. import tools 
import logging
logger = logging.getLogger(__name__)

import numpy as np

try:
	import f2n
except ImportError:
	logger.debug("Could not import f2n, no problem if you don't use it. You can find it here: http://obswww.unige.ch/~tewes/f2n_dot_py/")


def pngstampgrid(img, cat, pngfilepath, xname="x", yname="y", stampsize=100, ncols=5, upsample=4, z1="auto", z2="auto"):
	"""
	I write a grid of stamps corresponding to your catalog in a png image, so that you can visualize those galaxies...
	For this I currently use the slightly outdated f2n module.
	
	:param img: either a galsim image or the filepath to a FITS image
	:param cat: an astropy table
	:param pngfilepath: path to where I should write my png file
	:param xname: colname for the x position (in pixel)
	:param yname: colname for y
	:param stampsize: size in pixels of the stamps I should extract
	:param ncols: how many columns ?
	:param upsample: by how much should I upsample the stamps ?
	:param z1: "z" scale low
	:param z2: "z" scale high
	
	"""
	
	
	if type(img) is str:
		logger.debug("You gave me a filepath, and I'm now loading the image...")
		img = tools.image.loadimg(img)
		
	n = len(cat)
	nrows = int(np.ceil(float(n)/float(ncols)))
	logger.info("Preparing %i x %i stamps of %i x %i pixels each..." % (ncols, nrows, stampsize, stampsize))	
	
	stamprows = []
	for nrow in range(nrows):
		stamprow = []
		for ncol in range(ncols):
			
			index = ncol + ncols*nrow
			if index < n: # Then we have a galaxy to show
				gal = cat[index]
				(x, y) = (gal[xname], gal[yname])
				(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
				npstamp = gps.array
				
				f2nstamp = f2n.f2nimage(numpyarray=npstamp, verbose=False)

				f2nstamp.setzscale(z1, z2)
				f2nstamp.makepilimage("log", negative = False)
				f2nstamp.upsample(upsample)
			
				txt = [
					"%i (%i, %i)" % (gal.index, x, y),
				]
				f2nstamp.writeinfo(txt, colour=255)
				
			else: # No more galaxies, we just fill the splot with a grey empty stamp.
				npstamp = np.zeros((stampsize, stampsize))
				f2nstamp = f2n.f2nimage(numpyarray=npstamp, verbose=False)
				f2nstamp.setzscale(-1.0, 1.0)
				f2nstamp.makepilimage("lin", negative = False)
				f2nstamp.upsample(4)
			
			
			stamprow.append(f2nstamp)
		stamprows.append(stamprow)
	f2n.compose(stamprows, pngfilepath)
	logger.info("Wrote %s" % (pngfilepath))
	
	
#def npstampgrid(img, catalog, xname="x", yname="y", stampsize=100):
#	"""
#	I build a numpy array with stamps, intended for visualization
#	"""
#
#	#n = len(catalog)
#	#nrows = int(np.ceil(n/10))
#	#big = np.zeros((10*stampsize, nrows*stampsize))
#	#print n, nrows
#	
#	stamplist = []
#	for gal in catalog:
#		(x, y) = (gal[xname], gal[yname])
#		(gps, flag) = getstamp(x, y, img, stampsize)
#		if flag != 0:
#			stamplist.append(np.zeros(stampsize, stampsize))
#		else:
#			stamplist.append(gps.array)
#	
#	big = np.vstack(stamplist)
#	return big


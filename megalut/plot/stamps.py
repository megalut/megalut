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
	logger.warning("Could not import f2n, no problem if you don't use it. You can find it here: http://obswww.unige.ch/~tewes/f2n_dot_py/")


def pngstampgrid(img, cat, pngfilepath, xname="x", yname="y", stampsize=100, ncols=5, upsample=4, z1="auto", z2="auto"):
	"""
	For this it uses the (slightly outdated) f2n.py module.

	:param img: either a galsim image or the filepath to a FITS image
	:param cat: an astropy table
	:param pngfilepath: the png file path to be written
	:param xname: colname for the x position (in pixel)
	:param yname: colname for y
	:param stampsize: stamp size (in pixels) to be extracted
	:param ncols: number of postage-stamp columns
	:param upsample: postage-stamp upsample rate
	:param z1: "z" scale low
	:param z2: "z" scale high
	
	"""
	
	
	if type(img) is str:
		logger.debug("Filepath given, loading the image...")
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
				
				# Crosshair:
				s = stampsize
				f2nstamp.drawline(s/2, s/4, l=30, t=np.pi/2.0)	
				f2nstamp.drawline(s/4, s/2, l=30, t=0.0)

				# Just for reference, some other stuff from previous MegaLUT versions:				
				#f2nstamp.drawrectangle(1, s-1, 1, s-1)	
				#f2nstamp.drawrectangle(140, s-140, 140, s-140, colour=(0,255,255))	
				# Showing the measured shape, in red
				#e = np.hypot(galaxy.gal_e1, galaxy.gal_e2)
				#t = 0.5*np.arctan2(galaxy.gal_e2, galaxy.gal_e1)
				#f2nstamp.drawline(x = s/4, y=s/4 , l=150*e, t=t, width=3, colour=(255,0,0))


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


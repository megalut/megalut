"""
General purpose unspecific helper functions
"""

import os
import cPickle as pickle
import astropy.io.fits

import numpy as np
import logging

logger = logging.getLogger(__name__)


	
def writepickle(obj, filepath, protocol = -1):
	"""
	I write your python object obj into a pickle file at filepath.
	If filepath ends with .gz, I'll use gzip to compress the pickle.
	Leave protocol = -1 : I'll use the latest binary protocol of pickle.
	"""
	if os.path.splitext(filepath)[1] == ".gz":
		import gzip
		pkl_file = gzip.open(filepath, 'wb')
	else:
		pkl_file = open(filepath, 'wb')
	
	pickle.dump(obj, pkl_file, protocol)
	pkl_file.close()
	logger.info("Wrote %s" % filepath)
	
	
def readpickle(filepath):
	"""
	I read a pickle file and return whatever object it contains.
	If the filepath ends with .gz, I'll unzip the pickle file.
	"""
	if os.path.splitext(filepath)[1] == ".gz":
		pkl_file = gzip.open(filepath,'rb')
	else:
		pkl_file = open(filepath, 'rb')
	obj = pickle.load(pkl_file)
	pkl_file.close()
	logger.info("Read %s" % filepath)
	return obj


def fromfits(filepath):
	"""
	Read simple 1-hdu FITS files -> numpy arrays, so that the indexes [x,y] follow the orientations of
	x, y on ds9, respectively.
	"""
	a = astropy.io.fits.getdata(filepath).transpose()
	logger.info("Read FITS images %s from file %s" % (a.shape, filepath))
	return a
	

def tofits(a, filepath):
	"""
	Writes a simply 2D numpy array to FITS, same convention.
	"""
	
	if os.path.exists(filepath):
		logger.warning("File %s exists, I will overwrite it!" % (filepath))

	astropy.io.fits.writeto(filepath, a.transpose(), clobber=1)
	logger.info("Wrote %s array to %s" % (a.shape, filepath))



def getstamp(x, y, bigimg, stampsize):
	import galsim
	"""
	I prepare a bounded galsim image stamp "centered" at position (x, y) of your input galsim image.
	You can use the array attribute of the stamp if you want to get the actual pixels.
	
	This assumes that the origin of bigimg is set to (0, 0) as done by loadimg()
	(This is the default for GalSim, but not for GREAT3 if I remember well).
	
	:returns: a tuple(stamp, flag)
	"""

	assert int(stampsize)%2 == 0 # checking that it's even

	xmin = int(np.round(x - 0.5)) - int(stampsize)/2
	xmax = int(np.round(x - 0.5)) + int(stampsize)/2 - 1
	ymin = int(np.round(y - 0.5)) - int(stampsize)/2
	ymax = int(np.round(y - 0.5)) + int(stampsize)/2 - 1
			
	assert ymax - ymin == stampsize - 1 # This is the GalSim convention, both extermas are "included" in the bounds.
	assert xmax - xmin == stampsize - 1
	
	# We check that these bounds are fully within the image
	if xmin < bigimg.getXMin() or xmax > bigimg.getXMax() or ymin < bigimg.getYMin() or ymax > bigimg.getYMax():
		return (None, 1) # Ugly, should maybe be implemented as raising an exception caught higher up!
		
	# We prepare the stamp
	bounds = galsim.BoundsI(xmin, xmax, ymin, ymax)
	stamp = bigimg[bounds] # galaxy postage stamp
	assert stamp.array.shape == (stampsize, stampsize)
	
	return (stamp, 0)

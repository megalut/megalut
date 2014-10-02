"""
General purpose unspecific helper functions
"""

import os
import cPickle as pickle
import astropy.io.fits
import gzip

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
	
def getstamp(x, y, img, stampsize):
	"""
	I prepare a mage stamp "centered" at position (x, y) of your input *numpy* image.
	You can use the array attribute of the stamp if you want to get the actual pixels.
	
	:param x: x position of the stamp "center" (i.e., the object), in pixels.
	:param y: 
	:param img: The numpy array from which I should extract the stamp
	:param stampsize: width = height of the stamp, in pixels. Has to be even. 
	
	:returns: a tuple(stamp, flag). Flag is 1 if the stamp could not be extracted, 0 otherwise.
	"""

	assert int(stampsize)%2 == 0 # checking that it's even

	# By MegaLUT's definition, a pixel is centered at 0.5,0.5
	dd=+.5
	xmin=int(round(x-dd-stampsize/2.))
	xmax=int(round(x-dd+stampsize/2.))
	ymin=int(round(y-dd-stampsize/2.))
	ymax=int(round(y-dd+stampsize/2.))
	
	# We check that these bounds are fully within the image
	if xmin < 0 or xmax > np.shape(img)[0] or ymin < 0 or ymax > np.shape(img)[1]:
		return (None, 1) # Ugly, should maybe be implemented as raising an exception caught higher up!
		
	# We prepare the stamp
	stamp=img[xmin:xmax,ymin:ymax]
	assert np.shape(stamp) == (stampsize, stampsize)
	
	return (stamp, 0)





"""
General purpose unspecific helper functions
"""

import os
import cPickle as pickle
import astropy.io.fits

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
	data = astropy.io.fits.getdata(filepath).transpose()
	logger.info("Read FITS images %s from file %s" % (data.shape, filepath))
	return data
	

def tofits(a, filepath):
	"""
	Writes a simply 2D numpy array to FITS, same convention.
	"""
	
	if os.exists(filepath):
		logger.warning("File %s exists, I will overwrite it!" % (filepath))

	astropy.io.fits.writeto(filepath, a.transpose(), clobber=1)
	logger.info("Wrote %s array to %s" % (data.shape, filepath))



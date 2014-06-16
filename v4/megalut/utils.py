import os
import cPickle as pickle
import pyfits
import numpy as np
import math

	
	
def writepickle(obj, filepath, verbose=False, protocol = -1):
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
	if verbose: print "Wrote %s" % filepath	
	
def readpickle(filepath, verbose=False):
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
	if verbose: print "Read %s" % filepath
	return obj


def fromfits(filepath):
    """
    Read simple 1-hdu FITS files -> numpy arrays, so that the indexes [x,y] follow the orientations of
    x, y on ds9, respectively.
    """
    #print filepath
    return pyfits.getdata(filepath).transpose()


def tofits(a, filepath):
    """
    Overwrites any existing file.
    """
    if os.access(filepath, os.R_OK):
        os.remove(filepath)
    pyfits.writeto(filepath, a.transpose(), clobber=1)


def get_filename(filepath):
	"""
	Returns the name of the file without the extension.
	"""
	import os
	return os.path.splitext(os.path.basename(filepath))[0]


def timedelta_total_seconds(td):
	"""
	Returns the number of seconds for the given datetime td
	timedelta.total_seconds is available from Python 2.7
	"""
	return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / float(10**6)

def rev(angle):
	twopi = 2.*np.pi
	angle = angle - (angle//twopi)*twopi
	if angle < 0. : angle += twopi
	return angle




def invcumtri(y, a, c, b):
	"""
	Inverse of the cumulative probabitiliy distribution of a triangle function...
	Useful for generating pseudo-random sersic indexes for simulations
	
	a, c, b are the 3 points of the triangular distrib:
	
	a---c--------b
	
	If y is a "random" number uniformely distributed between 0 and 1, my return value is distributed in triangle a c b.
	
	Function computed based on the info from :
	http://en.wikipedia.org/wiki/Triangular_distribution
	"""

	assert b > a and c > a and c < b
	assert (y >= 0.0) and (y <= 1.0)
	
	if y <= (c-a)/(b-a):
		return math.sqrt(y*(b-a)*(c-a)) + a
	else:
		return b - math.sqrt((1.0-y)*(b-a)*(b-c))



def clipg(g1, g2, gmax=0.9):
	"""
	I numpy-clip g1 and g2 so that the module of g is below gmax.
	"""
	
	modg = np.hypot(g1, g2)
	clipmodg = np.clip(modg, 0.0, gmax)
	
	fact = clipmodg / modg
	
	return (g1*fact, g2*fact)
	
	
	
	
	
	
	


	








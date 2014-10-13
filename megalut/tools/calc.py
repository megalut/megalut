"""
A module to hold some maths or statistics oriented functions.
"""

import numpy as np

def rms(tru, pre):
	"""
	Returns the RMSD between two numpy arrays
	
	http://en.wikipedia.org/wiki/Root-mean-square_deviation
	
	"""
	return np.sqrt(np.mean((tru - pre)**2.0))




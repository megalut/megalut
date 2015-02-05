"""
General helper functions for shape measurements
"""
import os
import glob
import re
import numpy as np
import galsim

import logging
logger = logging.getLogger(__name__)

def simmeasdict(measdir, simparams):
	"""
	Function to help you explore available measurements of simulations obtained by :func:`megalut.meas.run.onsims`
	for a given measdir and simparams.
	So this function is here to "glob" the random file names for you.
	
	:param measdir: See :func:`megalut.meas.run.onsims`
	:param simparams: idem
	
	Regular expressions are used for this to avoid making optimistic assumptions about these filenames.
	A dict is returned whose keys are the simulated catalog names, and the corresponding entries
	are lists of filenames of the pkls with the measurements on the different realizations for each catalog. 
	
	An example of a dict that is returned::
		
		{'20141020T141239_E8gh8u':
			['20141020T141239_E8gh8u_0_galimg_meascat.pkl',
			 '20141020T141239_E8gh8u_1_galimg_meascat.pkl',
			 '20141020T141239_E8gh8u_2_galimg_meascat.pkl'],
		 '20141020T141239_9UhtkX':
		 	['20141020T141239_9UhtkX_0_galimg_meascat.pkl',
			 '20141020T141239_9UhtkX_1_galimg_meascat.pkl',
			 '20141020T141239_9UhtkX_2_galimg_meascat.pkl']
		}

	"""
	
	incatfilepaths = sorted(glob.glob(os.path.join(measdir, simparams.name, "*_galimg_meascat.pkl")))
	basenames = map(os.path.basename, incatfilepaths)
	
	if len(incatfilepaths) == 0:
		raise RuntimeError("No meascat found in %s" % (os.path.join(measdir, simparams.name)))
	
	# Here is how they look: 20141020T141239_9UhtkX_0_galimg_meascat.pkl
	# We get a unique list of the catalog names, using regular expressions
	
	p = re.compile("(\w*_\w*)_(\d*)_galimg_meascat.pkl")
	
	matches = [p.match(basename) for basename in basenames]
	if None in matches:
		raise RuntimeError("Some files in '%s' have unexpected filenames, something is wrong!" % (measdir))
		
		
	namereatuples = [(match.group(0), match.group(1), match.group(2)) for match in matches]
	# This gives (full file name, catname, realization number)
	
	catnames = sorted(list(set([namereatuple[1] for namereatuple in namereatuples])))
	
	out = {}
	for catname in catnames:
		out[catname] = [namereatuple[0] for namereatuple in namereatuples if namereatuple[1] == catname]
	
	logger.info("Found %i catalogs, and %i realizations (%.1f per catalog, on average)" %
		(len(catnames), len(namereatuples), float(len(namereatuples))/float(len(catnames))))
	
	return out


def mad(nparray):
	"""
	The Median Absolute Deviation
	http://en.wikipedia.org/wiki/Median_absolute_deviation

	Multiply this by 1.4826 to convert into an estimate of the Gaussian std.
	"""

	return np.median(np.fabs(nparray - np.median(nparray)))



def skystats(stamp):
	"""
	I measure some statistics of the pixels along the edge of an image or stamp.
	Useful to measure the sky noise, but also to check for problems. Use "mad"
	directly as a robust estimate the sky std.

	:param stamp: a galsim image, usually a stamp

	:returns: a dict containing "std", "mad", "mean" and "med"
	
	Note that "mad" is already rescaled by 1.4826 to be comparable with std.
	"""
	
	if isinstance(stamp, galsim.Image):
		a = stamp.array
		# Normally there should be a .transpose() here, to get the orientation right.
		# But in the present case it doesn't change anything, and we can skip it.
	else:
		a = stamp # Then we assume that it's simply a numpy array.
	
	edgepixels = np.concatenate([
			a[0,1:], # left
			a[-1,1:], # right
			a[:,0], # bottom
			a[1:-1,-1] # top
			])
	assert len(edgepixels) == 2*(a.shape[0]-1) + 2*(a.shape[0]-1)

	# And we convert the mad into an estimate of the Gaussian std:
	return {
		"std":np.std(edgepixels), "mad": 1.4826 * mad(edgepixels),
		"mean":np.mean(edgepixels), "med":np.median(edgepixels)
		}

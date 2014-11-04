"""
General helper functions for shape measurements
"""
import os
import glob
import re

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



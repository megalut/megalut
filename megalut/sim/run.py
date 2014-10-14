"""
High-level functions to make a whole set of simulations.

These functions write their results to disk, and therefore **define a directory and
filename structure**, containing the different realizations, catalogs, etc.
This is very different from the lower-level functions such as those in stampgrid.
"""

import os
import sys
import glob
import datetime
import tempfile
import cPickle as pickle

import stampgrid

import logging
logger = logging.getLogger(__name__)


def multi(params, drawcatkwargs, drawimgkwargs, ncat=2, nrea=2, ncpu=4, simdir="sim"):
	"""
	
	Uses stampgrid.drawcat and stampgrid.drawimg to draw several (ncat) catalogs
	and several (nrea) "image realizations" per catalog.
	I support multiprocessing!
	And if you want even more sims, just call me again!
	
	I take care of generating unique filenames (avoiding "race hazard") using tempfile.
	So you could perfectly have multiple processes running this function in parallel.
	However I also use include the datetime in my filenames, to make things more readable.
	
	
	drawcat -> make several realizations [drawimg, drawimg, drawimg]
	
	
	:param params: a sim.Params instance that defines the distributions of parameters
	
	
	:param ncat: The number of catalogs I should draw
	:param nrea: The number of realizations per catalog I should draw.
	
	
	:param ncpu: limit to the number of processes I should use.
	
	:param simdir: path to a directory where I should write the simulations.
		This directory has *not* to be unique for every call of this function!
		I will make subdirectories reflecting the name of your params inside.
		If this directory already exists, I will **add** my simulations to it, instead
		of overwriting anything.
	
	All further kwargs are passed to stampgrid.drawimg
	
	
	"""

	workdir = os.path.join(simdir, params.name)
	if not os.path.exists(workdir):
		os.makedirs(workdir)
		logger.info("Creating a new set of simulations named '%s'" % (params.name))
	else:
		logger.info("I'm adding new simulations to the existing set '%s'" % (params.name))

	logger.info("I will draw %i catalogs, and %i image realizations per catalog" % (ncat, nrea))

	# We create the catalogs, there is probably no need to parallelize this: 
	catalogs = [stampgrid.drawcat(params, **drawcatkwargs) for i in range(ncat)]

	# Now we save them usign single filenames.
	# This is not done with a timestamp ! The timestamp is only here to help humans.
	# The module tempfile takes care of making the filename unique.
	
	timecode = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
	prefix = "cat_%s_" % (timecode)
	
	for catalog in catalogs:
		catfile = tempfile.NamedTemporaryFile(mode='wb', prefix=prefix, suffix=".pkl", dir=workdir, delete=False)
		catalog.meta["filename"] = str(catfile.name)
		pickle.dump(catalog, catfile) # We directly use this open file object.
		catfile.close()
		logger.info("Wrote catalog into '%s'" % catalog.meta["filename"])

	
	# And now we draw the realizations for those catalogs.
	# This is done with multiprocessing
	
	
	
	
	
	

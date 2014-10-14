"""
High-level functions to make a whole set of simulations.

These functions write their results to disk, and therefore **define a directory and
filename structure**, containing the different realizations, catalogs, etc.
This is very different from the lower-level functions such as those in stampgrid.
"""

import os
import sys

import logging
logger = logging.getLogger(__name__)




def multi(params, drawcatkwargs, drawimgkwargs, ncat=2, nrea=2, ncpu=4, simdir="sim"):
	"""
	
	Uses stampgrid.drawcat and stampgrid.drawimg to get several catalogs
	and several realizations per catalog.
	I support multiprocessing!
	And if you want even more sims, just call me again!
	
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

	logger.info("I'm setting up to ")


	catalogs =


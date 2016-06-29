"""
Functions to group and summarize measurements accross multiple realizations of simulations.

"""
import os
import sys

import astropy
import numpy as np
import datetime

from .. import tools
import utils

import logging
logger = logging.getLogger(__name__)

def onsims(measdir, simparams, task="groupstats", **kwargs):
	"""
	Top-level function to group measurements as obtained from :func:`megalut.meas.run.onsims`.
	
	This function first explores the files in your measdir using :func:`simmeasdict`,
	then uses :func:`groupstats` or :func:`group` to "hstack" the different realizations catalog by catalog (and maybe compute some statistics),
	and finally it "vstacks" all your catalogs to return a single output table.

	:param measdir: See :func:`megalut.meas.run.onsims`
	:param simparams: idem
	:param task: either "groupstats" or "group", depending on what you want to do.
	:param kwargs: any further keyword arguments are passed to :func:`megalut.tools.table.groupstats` or :func:`megalut.tools.table.group`
	
	To learn about the output, see the latter.
	
	"""
	
	logger.info("Harvesting measurements of the simulations '%s' from %s" % (simparams, measdir))
	# We use the above function to find what we have:
	catdict = utils.simmeasdict(measdir, simparams)
	
	# We iterate over one simulated catalog after the other.
	outputcats = []
	for (catname, meascatfilepaths) in catdict.items():
		
		# So this are the measurements for a single catalog:
		logger.info("Reading all measurements for catalog '%s' (%i realizations)..." % (catname, len(meascatfilepaths)))
		meascats = [tools.io.readpickle(os.path.join(measdir, simparams.name, meascatfilepath)) for meascatfilepath in meascatfilepaths]
		
		# To avoid meta conflicts, we remove the meta from all but the first realization:
		for meascat in meascats[1:]:
			meascat.meta = {}
		# We also remove meta["img"] from the first realization, as it does no longer apply after the groupstats.
		meascats[0].meta.pop("img")
		
		if task == "groupstats":
			# And we call groupstats
			logger.info("Grouping columns and computing averages for catalog '%s'..." % (catname))
			grouped = tools.table.groupstats(meascats, **kwargs)
			outputcats.append(grouped)
		
		elif task == "group":
			logger.info("Grouping columns for catalog '%s'..." % (catname))
			grouped = tools.table.group(meascats, **kwargs)
			outputcats.append(grouped)
	
		else:
			raise RuntimeError("Unknown task!")	
	
	# And finally, we stack all these catalogs "vertically", to get a single one.
	# This is only to be done if we have several catalogs. In fact, vstack crashes if only 
	# one catalog is present.
	
	if len(outputcats) > 1:
	
		# Before vstacking, we check some meta for compatibility
		nmetaname = "n" + task # So this is either ngroup or ngroupstats
		assert nmetaname in outputcats[0].meta
			
		# All catalogs should have the same number of realizations
			
		ngroupstats = outputcats[0].meta[nmetaname]
		for outputcat in outputcats:
			if outputcat.meta[nmetaname] != ngroupstats:
				raise RuntimeError("Catalogs with different numbers of realizations should not be merged, clean your measdir accordingly!")
		
		# Now that checks are done, we have to remove some of the meta, to avoid conflicts (and keep thinks logical)
		for outputcat in outputcats[1:]: # On all but the first one, we remove everything.
			outputcat.meta = {}
		outputcats[0].meta.pop("catname", None) # after the merge, a single catname has no meaning anymore
		outputcats[0].meta.pop("psf", None) # There is no single "psf" anymore.
		outputcats[0].meta.pop("imgreas", None) # Idem
		
		logger.info("Concatenating catalogs...")
		outputcat = astropy.table.vstack(outputcats, join_type="exact", metadata_conflicts="error")
	
	else:
		logger.debug("Only one catalog, no need to call vstack")
		outputcat = outputcats[0]
	
	logger.info("Done with collecting results for %i simulated galaxies" % (len(outputcat)))
	
	return outputcat



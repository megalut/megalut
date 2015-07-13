"""
A measfct which computes statistics about the sky noise/level, using the edge of stamps

"""

import numpy as np
import copy
import astropy.table

import logging
logger = logging.getLogger(__name__)

import utils
from .. import tools


def measfct(cat, runon="img", prefix="", stampsize=None):
	"""
	
	:param runon: "img" or "psf" or ... -- decides on which image this should run.
		You might want to adjust the prefix accordingly.
	:param prefix: a prefix for the new column names. By default, no prefix is used.
	:param stampsize: if None, uses the image's stampsize.
	
	"""

	# Get the stampsize to be used:
	stampsize = cat.meta[runon].get_stampsize(stampsize)

	# Load the image:
	img = cat.meta[runon].load()
	
	# Prepare the catalog: THIS SHOULD BE REVIEWED ONCE WE ALL ADOPT ASTROPY 1.0 AND A RECENT NUMPY !
	cat = astropy.table.Table(copy.deepcopy(cat), masked=True) # Convert the table to a masked table
	# A bit stange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.

	cat.add_columns([
		astropy.table.Column(name=prefix+"skyflag", data=np.zeros(len(cat), dtype=int)), # We will always have a flag
		astropy.table.MaskedColumn(name=prefix+"skystd", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"skymad", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"skymean", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"skymed", dtype=float, length=len(cat)),
		astropy.table.MaskedColumn(name=prefix+"skystampsum", dtype=float, length=len(cat)),
	])
	for col in ["skystd", "skymad", "skymean", "skymed", "skystampsum"]:
		cat[prefix+col].mask = [True] * len(cat)
		
	
	# And now the loop
	for gal in cat:
		
		# Some simplistic progress indication:
		if gal.index%5000 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(len(cat)), gal.index, len(cat)))
		
		(x, y) = (gal[cat.meta[runon].xname], gal[cat.meta[runon].yname])
		(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
		
		if flag != 0:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"skyflag"] = flag
		
		else:
			out = utils.skystats(gps)
			gal[prefix + "skystd"] = out["std"]
			gal[prefix + "skymad"] = out["mad"]
			gal[prefix + "skymean"] = out["mean"]
			gal[prefix + "skymed"] = out["med"]
			gal[prefix + "skystampsum"] = out["stampsum"]
			
	
	nfailed = np.sum(cat[prefix + "skyflag"] > 0)
	if nfailed != 0:
		logger.warning("The stamp extraction failed on %i out of %i sources (%.1f percent)" % (nfailed, len(cat), 100.0*float(nfailed)/float(len(cat))))
	
	return cat

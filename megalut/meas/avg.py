"""
Functions to group and summarize measurements accross multiple realizations of simulations.

"""
import os
import sys

import astropy
import numpy as np

from .. import tools
import utils

import logging
logger = logging.getLogger(__name__)

def onsims(measdir, simparams, **kwargs):
	"""
	Top-level function to group measurements as obtained from :func:`megalut.meas.run.onsims`.
	
	This function first explores the files in your measdir using :func:`simmeasdict`,
	then uses :func:`groupstats` to "hstack" the different realizations catalog by catalog and compute the statistics,
	and finally it "vstacks" all your catalogs to return a single output table.

	:param measdir: See :func:`megalut.meas.run.onsims`
	:param simparams: idem
	:param kwargs: any further keyword arguments are passed to :func:`groupstats`
	
	To learn about the output, see :func:`groupstats`.
	
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
		
		# And we call groupstats
		logger.info("Grouping columns and computing averages for catalog '%s'..." % (catname))
		grouped = groupstats(meascats, **kwargs)
		outputcats.append(grouped)
	
	# And finally, we stack all these catalogs "vertically", to get a single one.
	# This is only to be done if we have several catalogs. In fact, vstack crashes if only 
	# one catalog is present.
	
	if len(outputcats) > 1:
	
		# Before vstacking, we check some meta for compatibility
		# All catalogs should have the same ngroupstats (== number of realizations)
		assert "ngroupstats" in outputcats[0].meta # was written by groupstats.
		ngroupstats = outputcats[0].meta["ngroupstats"]
		for outputcat in outputcats:
			if outputcat.meta["ngroupstats"] != ngroupstats:
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




def groupstats(incats, groupcols=None, removecols=None, removereas=True):
	"""
	This function "horizontally" merges input catalogs having the same columns by "hstacking" some of them (groupcols).
	Then, for each colname in groupcols, the function computes new statistics columns:
	
	- **colname_mean**: the average of colname from the different incats (skipping masked measurements)
	- **colname_med**: the median
	- **colname_std**: the sample standard deviation
	- **colname_n**: the number of available (that is, unmasked) measurements
		From this ``n``, you could compute the statistical error on the mean (``std/sqrt(n)``),
		or the success fraction of the measurement (``n/output.meta["ngroupstats"]``).
	
	:param incats: list of input catalogs (astropy tables, usually masked).
		They must all have identical order and columns (this will be checked).
	:param groupcols: list of column names that should be grouped, that is the columns that differ from incat to incat.
	:param removecols: list of column names that should be discarded
	:param removereas: if True, the individual realization columns in the output table will not be kept.
	
	The function tests that **any column which is not in groupcols or removecols is indeed IDENTICAL among the incats**.
	It could be that this leads to perfomance issues one day, but in the meantime it should make things safe.
	"""
	if groupcols is None:
		groupcols = []
	if removecols is None:
		removecols = [] 

	# First, some checks on the incats:
	colnames = incats[0].colnames # to check colnames
	
	for incat in incats:
		if incat.colnames != colnames:
			raise RuntimeError("Your input catalogs do not have the same columns: \n\n %s \n\n is not \n\n %s"
				% (incat.colnames, colnames))
		
		if incat.masked is False:
			logger.critical("Unmasked incats given (OK, but unexpected)")

	for groupcol in groupcols:
		if groupcol not in colnames:
			raise RuntimeError("The column '%s' which should be grouped is not present in the catalog. The availble column names are %s" % (groupcol, colnames))
		if groupcol in removecols:
			raise RuntimeError("Cannot both group and remove column '%s' " % groupcol)
			
	# We make a list of the column names that should stay unaffected:
	fixedcolnames = [colname for colname in colnames if (colname not in groupcols) and (colname not in removecols)]
	
	# We will take those columns from the first incat (we test later that this choice doesn't matter)
	outcat = incats[0][fixedcolnames] # This makes a copy
	
	
	# We test that the columns of these fixedcolnames are the same for all the different incats
	for incat in incats:
		if not np.all(incat[fixedcolnames] == outcat):
			raise RuntimeError("Something fishy is going on: some columns are not identical among %s. Add them to groupcols or removecols." % outcat.colnames)
	
	
	# Now we prepare subtables containing *only* the groupcols:
	subincats = [incat[groupcols] for incat in incats]
	# We remove all meta from these subincats:
	for subincat in subincats:
		subincat.meta = {}
	
	# We prepare some "suffixes" for these columns. For this we do not try to reuse the int from the realization filename
	# Indeed, the user could have delete some realizations etc, leading to quite a mess.
	# It's easier to just make a new integer range:
	incat_names = ["%i" % (i) for i in range(len(subincats))]
	
	# We use hstack to collect all these columns into a single table, adding these incat_names as suffixes to the column names.
	togroupoutcat = astropy.table.hstack(subincats, join_type="exact",
		table_names=incat_names, uniq_col_name="{col_name}_{table_name}", metadata_conflicts="error")
	
	# At this point, this table just contains the individual groupcols from the incats.
	# For each groupcol, we now compute some statistics, and add them as new columns
	for groupcol in groupcols:
			
		suffixedcolnames = ["%s_%s" % (groupcol, incat_name) for incat_name in incat_names]
		# So this looks like adamom_flux_1, adamom_flux_2, ...
		
		# We build a masked numpy array with the data of these columns
		# Maybe this can be done in a better way ?
		numpycolumns = [np.ma.array(togroupoutcat[suffixedcolname]) for suffixedcolname in suffixedcolnames]
		array = np.ma.array(numpycolumns)
		
		# And compute the stats:
		togroupoutcat["%s_mean" % (groupcol)] = np.ma.mean(array, axis=0)
		togroupoutcat["%s_med" % (groupcol)] = np.ma.median(array, axis=0)
		togroupoutcat["%s_std" % (groupcol)] = np.ma.std(array, axis=0)
		togroupoutcat["%s_n" % (groupcol)] = np.ma.count(array, axis=0)
		
		# We remove the individual columns, if asked for
		if removereas:
			togroupoutcat.remove_columns(suffixedcolnames)
		
	
	# Finally, we add the fixedcolname-columns to the table:
	outputcat = astropy.table.hstack([outcat, togroupoutcat], join_type="exact",
		table_names=["SHOULD_NOT_BE_SEEN", "SHOULD_NEVER_BE_SEEN"], uniq_col_name="{col_name}_{table_name}", metadata_conflicts="error")
	
	# And we save the number of catalogs that got grouped (should usually be nrea):
	outputcat.meta["ngroupstats"] = len(incats)
	
	return outputcat






#class Operation():
#	"""
#	Class to hold the column name and the type of operation to perform
#	"""
#	
#	def __init__(self, incolname, outcolname, optype="avg"):
#		
#		self.incolname = incolname
#		self.outcolname = outcolname
#		if optype not in ["avg"]:
#			raise RuntimeError("Unknown optype")
#		self.optype = optype
#		
#		
#def general(incats, operations, idcolname="id"):
#	"""
#	
#	:param incats: a list of input catalogs (astropy tables)	
#	:param operations: a list of Operation objects defining what should be done
#	
#	:param idcolname: I use this column to cross-identify galaxies between the different catalogs
#		Set this to None if you don't want me to check the ids, and just assume your catalogs are
#		all sorted in the same way.
#	
#	:returns: an output catalog
#	"""
#	
#	
#	# Sort input catalogs using idcolname
#	
#
#	for operation in operations:
#		
#		pass
#		

	



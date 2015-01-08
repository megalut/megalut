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




def groupstats(incats, groupcols=None, removecols=None, removereas=True, keepfirstrea=True):
	"""
	This function computes simple statistics "across" corresponding columns from the list of input catalogs (incats).
	For each colname in groupcols, the function computes:
	
	- **colname_mean**: the average of colname from the different incats (skipping masked measurements)
	- **colname_med**: the median (idem)
	- **colname_std**: the sample standard deviation (idem)
	- **colname_n**: the number of available (that is, unmasked) measurements
		From this ``n``, you could compute the statistical error on the mean (``std/sqrt(n)``),
		or the success fraction of the measurement (``n/output.meta["ngroupstats"]``).
	
	:param incats: list of input catalogs (astropy tables, usually masked).
		They must all have identical order and column names (this will be checked).
	:param groupcols: list of column names that should be "grouped", that is the columns that differ from incat to incat.
	:param removecols: list of column names that should be discarded in the output catalog
	:param removereas: if True, the individual realization columns in the output table will **not** be kept in the ouput
		(except maybe the first one, see keepfirstreas).
		Setting this to False can result in very bulky catalogs.
	:param keepfirstreas: if True, the values of the first realization ("_0") will be kept.
		It is usually handy (and not too bulky) to "keep" one single realization in the output catalog.
	
	The function tests that **any column which is not in groupcols or removecols is indeed IDENTICAL among the incats**.
	It could be that this leads to perfomance issues one day, but in the meantime it should make things safe.
	
	Developer note: it is slow to append columns to astropy tables (as this makes a copy of the full table).
		So we try to avoid this as much as possible here, and use masked numpy arrays and hstack.
	
	"""
	
	starttime = datetime.datetime.now()
	
	if groupcols is None:
		groupcols = []
	if removecols is None:
		removecols = [] 

	# First, some checks on the incats:
	if len(incats) < 2:
		raise RuntimeError("Statistics can only be computed if several incats are given.")
	
	colnames = incats[0].colnames # to check colnames
	
	for incat in incats:
		if incat.colnames != colnames:
			raise RuntimeError("Your input catalogs do not have the same columns: \n\n %s \n\n is not \n\n %s"
				% (incat.colnames, colnames))
		
		if incat.masked is False:
			logger.critical("Input catalogs are not masked (OK for me, but unexpected)")

	for groupcol in groupcols:
		if groupcol not in colnames:
			raise RuntimeError("The column '%s' which should be grouped is not present in the catalog. The availble column names are %s" % (groupcol, colnames))
		if groupcol in removecols:
			raise RuntimeError("Cannot both group and remove column '%s' " % groupcol)
			
	# We make a list of the column names that should stay unaffected:
	fixedcolnames = [colname for colname in colnames if (colname not in groupcols) and (colname not in removecols)]
	
	if len(fixedcolnames) > 0:
		# We will take those columns from the first incat (we test below that this choice doesn't matter)
		fixedcat = incats[0][fixedcolnames] # This makes a copy
	
		# We test that the columns of these fixedcolnames are the same for all the different incats
		for incat in incats:
			if not np.all(incat[fixedcolnames] == fixedcat):
				raise RuntimeError("Something fishy is going on: some columns are not identical among %s. Add them to groupcols or removecols." % outcat.colnames)
		logger.debug("Done with testing the identity of all the common columns")
	
	# We prepare some "suffixes" to use when mixing colums of the incats.
	# For this we do not try to reuse the int from the realization filename
	# Indeed, the user could have delete some realizations etc, leading to quite a mess.
	# It's easier to just make a new integer range:
	incat_names = ["%i" % (i) for i in range(len(incats))]

	statscatdict = {} # We will add statistics columns (numpy arrays) to this list
	statscatdictnames = [] # Is used to keep a nice ordering
	reascats = [] # We might put single-realization columns here
	
	# For each groupcol, we now compute some statistics
	for groupcol in groupcols:
		logger.debug("Computing stats for '%s'" % (groupcol))
		suffixedcolnames = ["%s_%s" % (groupcol, incat_name) for incat_name in incat_names]
		# So this looks like adamom_flux_1, adamom_flux_2, ...
		
		# We build a masked numpy array with the data of these columns
		array = np.ma.vstack([incat[groupcol] for incat in incats])
		# first index is incat, second is row
		
		# And compute the stats:
		statscatdict["%s_mean" % (groupcol)] = np.ma.mean(array, axis=0)
		statscatdict["%s_med" % (groupcol)] = np.ma.median(array, axis=0)
		statscatdict["%s_std" % (groupcol)] = np.ma.std(array, axis=0)
		statscatdict["%s_n" % (groupcol)] = np.ma.count(array, axis=0)
		# We also add those names to a list:
		statscatdictnames.extend(["%s_mean" % (groupcol), "%s_med" % (groupcol), "%s_std" % (groupcol), "%s_n" % (groupcol)])
		
		# Depening on the removereas and keepfirstreas flags, we also keep some columns
		# from the individual realizations.
		if removereas == False:
			# We keep every column:
			reascats.append(astropy.table.Table([incat[groupcol] for incat in incats], names = suffixedcolnames))
			 
		else:
			# see if we should keep the first:
			if keepfirstrea == True:
				# keep the first
				reascats.append(astropy.table.Table([incat[groupcol] for incat in [incats[0]]], names = [suffixedcolnames[0]]))
			
	assert len(statscatdict) == 4*len(groupcols) # Just a check, as in principle stuff in the dict could be overwritten.

	# We now make a table out of the statscatdict :
	statscat = astropy.table.Table(statscatdict, names=statscatdictnames)
	
	# We add individual realization data (if needed) :
	if len(reascats) != 0:
		statscat = astropy.table.hstack([statscat] + reascats, join_type="exact",
		metadata_conflicts="error")
	
	# Finally, we prepend the fixedcolname-columns to the table:
	if len(fixedcolnames) > 0:
		outputcat = astropy.table.hstack([fixedcat, statscat], join_type="exact",
			table_names=["SHOULD_NOT_BE_SEEN", "SHOULD_NEVER_BE_SEEN"], uniq_col_name="{col_name}_{table_name}", metadata_conflicts="error")
	else:
		outputcat = statscat

	# And we save the number of catalogs that got grouped (should usually be nrea):
	outputcat.meta["ngroupstats"] = len(incats)

	endtime = datetime.datetime.now()
	logger.debug("The groupstats computations took %s" % (str(endtime - starttime)))
	logger.debug("Output table: %i rows and %i columns (%i common, %i computed, %i reas)" %
		(len(outputcat), len(outputcat.colnames), len(fixedcolnames), len(statscatdict), len(statscat.colnames)-len(statscatdict)))
	
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

	



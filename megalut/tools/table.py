"""
Helpers for astropy.table arrays
"""

import numpy as np
import astropy.table
import datetime

import logging
logger = logging.getLogger(__name__)


def hjoin(table1, table2, idcol):
	"""
	This is a safe way to "hstack" two astropy tables containing different columns
	for the same sources, using a specified "ID" column.
	
	These kind of things are easy to do with astropy tables.
	The present function is just a wrapper for one type of operation that is very
	frequently required when running MegaLUT.

	Instead of a simple hstack (which would rely on the order of rows), here we use 
	join to match the rows, using the idcol (i.e., "ID") column.
	We guarantee that the ouput table will have the same number of
	rows as the input tables.
	
	This function could be made more general/powerful (as join is much more general),
	but it is kept simple on purpose.
	
	:param table1: an astropy table
	:param table2: an astropy table
	:param idcol: a column label, to be used as key for the identification
	              (must exist in both tables)
	
	If there are columns that have the same label in both table1 and table2, the column values
	will be taken from table1, so as to avoid duplicated columns in the resulting AstroPy table.
	
	"""

	logger.debug("Starting some security checks (%i rows)..." % len(table1))
	
	if len(table1) != len(table2):
		raise RuntimeError("Your tables do not have the same row counts!")
	
	
	if idcol not in table1.colnames:
		raise RuntimeError("There is no ID column '%s' in table1" % (idcol))
	if idcol not in table2.colnames:
		raise RuntimeError("There is no ID column '%s' in table2" % (idcol))
		
	set1 = set(table1[idcol])
	set2 = set(table2[idcol])
	if len(set1) != len(table1):
		raise RuntimeError("The IDs in table1 are not unique!")
	if len(set2) != len(table2):
		raise RuntimeError("The IDs in table2 are not unique!")
	if set1 != set2:
		raise RuntimeError("The IDs in the two tables are not identical!")
		
	# Now we find out which cols to keep in table2 when calling join
	# (without changing table2 of course).
	
	commoncols = [col for col in table1.colnames if col in table2.colnames]
	if len(commoncols) > 1: # Otherwise it's just the idcol...
		logger.info("The column labels %s are common, values from table1 will be kept." % (str(commoncols)))
	table2colstokeep = [col for col in table2.colnames if col not in commoncols]
	table2colstokeep.append(idcol)
	
	# Indeed, join would duplicate and rename common columns (even if they contain the same values)
	# Unless keys = None, in which case it would use them to identify.
	# But then, if those cols are different, the identification fails and join would silently keep
	# the "left" data, with masked values for the columns of table2 (as if "not found")
	# That's not what we want.
	# What we want is to raise an Error if the idcol values are fishy.
	
	logger.debug("Done with security checks")
	
	output = astropy.table.join(table1, table2[table2colstokeep], keys=idcol,
		join_type='left', metadata_conflicts="error")

	assert len(output) == len(table1)
	assert len(output.colnames) == len(table1.colnames) + len(table2colstokeep) - 1
	
	return output
	

def shuffle(table):
	"""
	Return a copy of the input table with randomly shuffled rows.
	Easy function, but it demonstrates one way of how this can be done.
	"""
	
	logger.debug("Shuffling a table of %i rows..." % len(table))
	
	indexes = np.arange(len(table))
	np.random.shuffle(indexes)
	return table[indexes] # This is a copy
	
	
	
def groupstats(incats, groupcols=None, removecols=None, removereas=True, keepfirstrea=True, checkcommon=True):
	"""
	This function computes simple statistics "across" corresponding columns from the list of input catalogs (incats).
	
	:param incats: list of input catalogs (astropy tables, usually masked).
		They must all have identical order and column names (this will be checked).
	:param groupcols: list of column names that should be "grouped", that is the columns whose content differ from incat to incat.
	:param removecols: list of column names that should be discarded in the output catalog
	:param removereas: if True, the individual realization columns in the output table will **not** be kept in the ouput
		(except maybe the first one, see keepfirstreas).
		Setting this to False can result in very bulky catalogs.
	:param keepfirstreas: if True, the values of the first realization ("_0") will be kept.
		It is usually handy (and not too bulky) to "keep" one single realization in the output catalog.
	:param checkcommon: if True (default), the function tests that **any column which is not in groupcols or removecols is indeed IDENTICAL among the incats**.
		This can lead to perfomance issues for catalogs with many (say > 1000) columns.
	
	For each colname in groupcols, the function computes:
	
	- **colname_mean**: the average of colname from the different incats (skipping masked measurements)
	- **colname_med**: the median (idem)
	- **colname_std**: the sample standard deviation (idem)
	- **colname_n**: the number of available (that is, unmasked) measurements
	
	The function returns a single catalog, and the above column names designate the new columns that will be added to this catalog.
	
	.. note:: The number of incats (which is the maximum possible value for "colname_n") is stored as meta["ngroupstats"]
		of each of the newly created columns.	
		When running on measurements obtained on different realizations, this "ngroupstats" allows for instance to compute
		the success fraction of the measurement:  outcat["foo_n"] / outcat["foo_n"].meta["ngroupstats"]  
		
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
		raise RuntimeError("Statistics can only be computed if more than one incats are given.")
	
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
	
		if checkcommon == True:
			# We test that the columns of these fixedcolnames are the same for all the different incats
			for incat in incats:
				if not np.all(incat[fixedcolnames] == fixedcat):
					raise RuntimeError("Something fishy is going on: some columns are not identical among %s. Add them to groupcols or removecols." % outcat.colnames)
			logger.debug("Done with testing the identity of all the common columns")
		else:
			logger.debug("Did not test the identity of all the common columns")
	
	# We prepare some "suffixes" to use when mixing columns of the incats.
	# For this we do not try to reuse the int from the realization filename
	# Indeed, the user could have deleted some realizations etc, leading to quite a mess.
	# It's easier to just make a new integer range:
	incat_names = ["%i" % (i) for i in range(len(incats))]

	statscatdict = {} # We will add statistics columns (numpy arrays) to this list
	statscatdictnames = [] # Is used to keep a nice ordering
	reascats = [] # We might put single-realization columns here
	
	# For each groupcol, we now compute some statistics
	for groupcol in groupcols:
		logger.info("Computing stats for '%s'" % (groupcol))
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
	
	# We add the number of catalogs that got grouped in the meta of every new "groupstats" column.
	# Strictly speaking this is where this information belongs, as it relates to the new columns, not to the catalog.
	# See note a few lines below.
	for colname in statscat.colnames:
		statscat[colname].meta["ngroupstats"] = len(incats)
	
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
	
	# Especially when averaging measurements on realizations, it seems ok to write ngroupstats also into the meta of the catalog itself.
	# So we keep doing this.
	outputcat.meta["ngroupstats"] = len(incats)

	endtime = datetime.datetime.now()
	logger.info("The groupstats computations took %s" % (str(endtime - starttime)))
	logger.info("Output table: %i rows and %i columns (%i common, %i computed, %i reas)" %
		(len(outputcat), len(outputcat.colnames), len(fixedcolnames), len(statscatdict), len(statscat.colnames)-len(statscatdict)))
	
	return outputcat



class Selector:
	
	def __init__(self, criteria, name):
		
		self.criteria = criteria
		self.name = name
		
		
	def select(self, cat):
		"""
		Returns those rows of cat that match all criteria
		"""
		pass
		return cat

	
	
	
	
	

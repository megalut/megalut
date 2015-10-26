"""
Helpers for astropy.table arrays
"""

import numpy as np
import astropy.table
import datetime

import copy

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
	





def group(incats, groupcols=None, removecols=None, checkcommon=True):
	"""
	Turns a list of catalogs (typically representing different realizations of the same galaxies) into a single "3D" catalog.
	This is somehow similar to groupstats, but here we do not compute any stats, and we don't modify column names.
		
	Returns an astropy table in which the groupcols columns are 2D arrays.
	
	This is easier to digest for Tenbilac etc than to carry around many columns _rea0, _rea1, ...
	
	"""
	starttime = datetime.datetime.now()
	
	if groupcols is None:
		groupcols = []
	if removecols is None:
		removecols = [] 

	# OK I'm taking here a few simple tests from from groupstats, as they are quite helpful.

	colnames = incats[0].colnames # to check colnames
	
	for incat in incats:
		if incat.colnames != colnames:
			raise RuntimeError("Your input catalogs do not have the same columns: \n\n %s \n\n is not \n\n %s"
				% (incat.colnames, colnames))

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
					raise RuntimeError("Something fishy is going on: some columns are not identical among %s. Add them to groupcols or removecols." % fixedcolnames)
			logger.debug("Done with testing the identity of all the common columns")
		else:
			logger.debug("Did not test the identity of all the common columns")

	outputcols = [] # We fill this with the new 2D columns...
	for groupcol in groupcols:
		#logger.info("Grouping '%s'" % (groupcol))
		
		# We build a masked numpy array with the data of these columns
		array = np.ma.vstack([incat[groupcol] for incat in incats]).transpose()
		
		#print array.shape # With this transpose, first index is galaxy, second is realization

		outputcols.append(astropy.table.MaskedColumn(array, name=groupcol))

	
	# We now make a table out of the outputcols :
	outputcat = astropy.table.Table(outputcols)
	
	# Finally, we prepend the fixedcolname-columns to the table:
	if len(fixedcolnames) > 0:
		outputcat = astropy.table.hstack([fixedcat, outputcat], join_type="exact",
			table_names=["SHOULD_NOT_BE_SEEN", "SHOULD_NEVER_BE_SEEN"], uniq_col_name="{col_name}_{table_name}", metadata_conflicts="error")
	
	# Especially when averaging measurements on realizations, it seems ok to write ngroupstats also into the meta of the catalog itself.
	# So we keep doing this.
	outputcat.meta["ngroup"] = len(incats)

	endtime = datetime.datetime.now()
	logger.info("The grouping took %s" % (str(endtime - starttime)))
	logger.info("Output table: %i rows and %i columns (%i common, %i grouped)" %
		(len(outputcat), len(outputcat.colnames), len(fixedcolnames), len(outputcols)))
	
	return outputcat



	
def groupstats(incats, groupcols=None, removecols=None, removereas=True, keepfirstrea=True, checkcommon=True):
	"""
	This function computes simple statistics "across" corresponding columns from the list of input catalogs (incats).
	Instead of producing 2D columns (i.e., a 3D table), it puts all the data into extra columns with custom names ("_rea0"...).
	
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
	
	notmasked = False
	for incat in incats:
		if incat.colnames != colnames:
			raise RuntimeError("Your input catalogs do not have the same columns: \n\n %s \n\n is not \n\n %s"
				% (incat.colnames, colnames))
		
		if incat.masked is False:
			notmasked = True
	
	if notmasked:
		logger.info("At least one of the input catalogs is not masked (OK but unexpected)")

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
					raise RuntimeError("Something fishy is going on: some columns are not identical among %s. Add them to groupcols or removecols." % fixedcolnames)
			logger.debug("Done with testing the identity of all the common columns")
		else:
			logger.debug("Did not test the identity of all the common columns")
	
	# We prepare some "suffixes" to use when mixing columns of the incats.
	# For this we do not try to reuse the int from the realization filename
	# Indeed, the user could have deleted some realizations etc, leading to quite a mess.
	# It's easier to just make a new integer range:
	incat_names = ["rea%i" % (i) for i in range(len(incats))]

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




def collapse(cat):
	"""
	Transforms a table into a new table with a single row, all the data being flattenend into the second dimension of each column.
	"""
	
	cols = []
	for colname in cat.colnames:
		
		data = np.ma.array(cat[colname]).flatten()
		assert data.ndim == 1
		data = data.reshape((1, data.size))
		cols.append(data)
		#print data.shape
	
	return astropy.table.Table(cols, names=cat.colnames)
	

def keepunique(cat, colnames=None, skipuniquetest=False):
	"""
	For each col in colnames, if the column is 2D (and the contents of each cell is identical),
	makes the column 1D by keeping only one of the identical values in each cell.
	If colnames is not specified, this is applied on all columns.
	"""
	
	
	if colnames == None:
		proccolnames = cat.colnames # We will just run on all of them
	else:
		proccolnames = colnames
		
	for colname in proccolnames:
		
		if colnames != None:
			logger.info("Keepuniquing column '{}'...".format(colname))
		
		if cat[colname].ndim == 2:
			
			#if skipuniquetest: # Then we do not check the cell contents, just pick the first elements:
			#else: # we do check the cell contents for uniqueness
			
			aresame = True
			if skipuniquetest == False:
				firstvals = cat[colname][:,0].data # All rows, but just first element of the second index
				tests = cat[colname].data.transpose() == firstvals			
				if not np.all(tests):
					aresame = False
			
			if aresame == True: # We just keep the first element in each cell:
				newcol = cat[colname][:,0]
				cat.remove_column(colname)
				cat[colname] = newcol # Is a bit weird, but otherwise it complains about non-matching shapes
				
			else: # We do not keepunique it, but warn the user
				if colnames != None: # So if the user did explicitly specify colnames:
					logger.warning("Cells of column '{}' do not contain identical values, cannot keepunique it!".format(colname))
	
		else:
			if colnames != None: # So if the user did explicitly specify colnames:
				logger.warning("Column '{}' is not 2D, cannot keepunique it!".format(colname))
		


def groupreshape(cat, groupcolnames):
	"""
	Rearranges the data in the table so to have only one row per different value combination of the diffcolnames.
	For each of these rows, all the data is collected in the second dimension.
	
	Ideally these groupcolanmes would not contain floats, but integers. But it seems to work with simple floats as well.
	
	"""
	
	# Start
	logger.info("Determining groups for {}...".format(groupcolnames))
	
	# Check that groupcolnames are 1D columns
	for colname in groupcolnames:
		if cat[colname].ndim != 1:
			raise RuntimeError("Only 1D columns are allowed as groupcolnames! '{}' is not.".format(colname))
	
	# Use the table group functionality
	groupcat = cat.group_by(groupcolnames)
	
	ngroups = len(groupcat.groups.indices) -1
	logger.info("Reshaping data in {} groups...".format(ngroups))
	
	collapsedgroups = []
	for (i, group) in enumerate(groupcat.groups):
		
		if i%10 == 0:
			logger.info("Working on group {}/{} of length {}...".format(i+1, len(groupcat.groups), len(group)))
		collapsedgroup = collapse(group) # This is a Table
		assert len(collapsedgroup) == 1
		
		collapsedgroups.append(collapsedgroup)
	
	# Some assert checks
	# Columns should have exactly the same dimensions in all of the collapsedgroups:
	colshapes = [collapsedgroups[0][col].shape for col in collapsedgroups[0].colnames]
	for t in collapsedgroups:
		assert t.colnames == collapsedgroups[0].colnames
		assert [t[col].shape for col in t.colnames] == colshapes
	
	# Now we can simply vstack this stuff.
	logger.info("Done with reshaping, now stacking...")
	outcat = astropy.table.vstack(collapsedgroups, join_type=u'exact', metadata_conflicts=u'error')
	assert len(outcat) == ngroups
	
	# At least for the groupcolnames, we only want to keep single values:
	keepunique(outcat, groupcolnames)
	
	return outcat
		
		

def addstats(cat, col, outcolprefix=None):
	"""
	Adds columns containing some statistics of the values in each cell of col.
	So this is for 2D columns. Togheter this the function "group", this replaces the old-style "groupstats".
	
	:param col: name of the (2D) column containing the data for which stats should be computed
	
	"""
	if outcolprefix == None:
		outcolprefix = col
		
	outcolnames = [outcolprefix + suffix for suffix in ["_mean", "_med", "_std", "_n"]]
	for outcolname in outcolnames:
		if outcolname in cat.colnames:
			raise RuntimeError("Column {} already exists, refusing to overwrite.".format(outcolname))
	
	if cat[col].ndim != 2:
		raise RuntimeError("Column '{}' is not 2-dimensional, stats do not make sense!".format(col))
		
	logger.info("Adding stats for column {} of shape {}...".format(col, cat[col].shape))
	
	cat[outcolprefix + "_mean"] = np.ma.mean(cat[col], axis=1)
	cat[outcolprefix + "_med"] = np.ma.median(cat[col], axis=1)
	cat[outcolprefix + "_std"] = np.ma.std(cat[col], axis=1)
	cat[outcolprefix + "_n"] = np.ma.count(cat[col], axis=1)
	
	


class Selector:
	"""
	Provides a simple way of getting "configurable" sub-selections of rows from a table.
	"""
	
	def __init__(self, name, criteria):
		"""
		
		:param name: a short string describing this selector (like "star", "low_snr", ...)
		:param criteria: a list of tuples describing the criteria. Each of these tuples starts 
			with a string giving its type, followed by some arguments.
	
			Illustration of the available criteria (all limits are inclusive):
		
			- ``("in", "tru_rad", 0.5, 0.6)`` : ``"tru_rad"`` is between 0.5 and 0.6 ("in" stands for *interval*) and *not* masked
			- ``("max", "snr", 10.0)`` : ``"snr"`` is below 10.0 and *not* masked
			- ``("min", "adamom_flux", 10.0)`` : ``"adamom_flux"`` is above 10.0 and *not* masked
			- ``("is", "Flag", 2)`` : ``"Flag"`` is exactly 2 and *not* masked
			- ``("nomask", "pre_g1")`` : ``"pre_g1"`` is not masked
			- ``("mask", "snr")`` : ``"snr"`` is masked
		
		
		"""
		self.name = name
		self.criteria = criteria
	
	def __str__(self):
		"""
		A string describing the selector
		"""
		return "'%s' %s" % (self.name, repr(self.criteria))
	
	
	def combine(self, *others):
		"""
		Returns a new selector obtained by merging the current one with one or more others.

		:param others: provide one or several other selectors as arguments.

		.. note:: This does **not** modify the current selector in place! It returns a new one!
		"""
	
		combiname = "&".join([self.name] + [other.name for other in others])
	
		combicriteria = self.criteria
		for other in others:
			combicriteria.extend(other.criteria)
	
		return Selector(combiname, combicriteria)
		
	
	def select(self, cat):
		"""
		Returns a copy of cat with those rows that satisfy all criteria.
		
		:param cat: an astropy table
		
		"""
		
		if len(self.criteria) is 0:
			logger.warning("Selector %s has no criteria!" % (self.name))
			return copy.deepcopy(cat)
		
		passmasks = []
		for crit in self.criteria:
		
			if cat[crit[1]].ndim != 1:
				logger.critical("Using Selector with multidimensional columns... at your own risk.")
			
			if crit[0] == "in":
				if len(crit) != 4: raise RuntimeError("Expected 4 elements in criterion %s" % (str(crit)))
				passmask = np.logical_and(cat[crit[1]] >= crit[2], cat[crit[1]] <= crit[3]).filled(fill_value=False)
				# Note about the "filled": if crit[2] or crit[3] englobe the values "underneath" the mask,
				# some masked crit[1] will result in a masked "passmask"!
				# But we implicitly want to reject masked values here, hence the filled.			
			elif crit[0] == "max":
				if len(crit) != 3: raise RuntimeError("Expected 3 elements in criterion %s" % (str(crit)))
				passmask = (cat[crit[1]] <= crit[2]).filled(fill_value=False)
			
			elif crit[0] == "min":
				if len(crit) != 3: raise RuntimeError("Expected 3 elements in criterion %s" % (str(crit)))
				passmask = (cat[crit[1]] >= crit[2]).filled(fill_value=False)
			
			elif crit[0] == "is":
				if len(crit) != 3: raise RuntimeError("Expected 3 elements in criterion %s" % (str(crit)))
				passmask = (cat[crit[1]] == crit[2]).filled(fill_value=False)
			
			elif (crit[0] == "nomask") or (crit[0] == "mask"):
				if len(crit) != 2: raise RuntimeError("Expected 2 elements in criterion %s" % (str(crit)))
				if hasattr(cat[crit[1]], "mask"): # i.e., if this column is masked:
					if crit[0] == "nomask":
						passmask = np.logical_not(cat[crit[1]].mask)
					else:
						passmask = cat[crit[1]].mask
				else:
					logger.warning("Criterion %s is facing an unmasked column!" % (str(crit)))
					passmask = np.ones(len(cat), dtype=bool)
			
			else:
				raise RuntimeError("Unknown criterion %s" % (crit))
					
			logger.debug("Criterion %s of '%s' selects %i/%i rows (%.2f %%)" %
				(crit, self.name, np.sum(passmask), len(cat), 100.0 * float(np.sum(passmask))/float(len(cat))))
			
			assert len(passmask) == len(cat)
			passmasks.append(passmask) # "True" means "pass" == "keep this"
		
		# Combining the passmasks:
		passmasks = np.logical_not(np.column_stack(passmasks)) # "True" means "reject"
		combimask = np.logical_not(np.sum(passmasks, axis=1).astype(bool)) # ... and "True" means "keep this" again.
		
		logger.info("Selector '%s' selects %i/%i rows (%.2f %%)" %
				(self.name, np.sum(combimask), len(cat), 100.0 * float(np.sum(combimask))/float(len(cat))))
		
		return cat[combimask]



# Deprecated. Use feature.cutmasked if you need that.
#
#def cutmasked(cat, colnames, keep_all_columns=True):
#	"""
#	Returns those rows of table for which all of the given colnames are unmasked.
#	To do this, it "combines" the masks from the different colnames.
#	This is in principle close to what **numpy.ma.compress_rows** does.
#	But here we also log a bit about the masked columns.
#	
#	:param cat: an astropy table
#	:param colnames: a list of column names whose data must be available in the output
#	:param keep_all_columns: if False, the returned table only contains the given colnames.
#	
#	:returns: an astropy table		
#	"""
#	# Some trivial tests:
#	for colname in colnames:
#		if colname not in cat.colnames:
#			raise RuntimeError("The column '%s' is not available among %s" % (colname, str(cat.colnames)))
#		
#		#assert cat[colname].ndim == 1 # This function has not been tested for anything else...
#		# No, this is now beginnign to get implemented...
#			
#	if len(colnames) != len(list(set(colnames))):
#		raise RuntimeError("Strange, some colnames appear multiple times in %s" % (str(colnames)))
#	
#	# First, get a list of 1D masks, one per column
#	
#	masklist = []
#	
#	print "Terrible hack, just uses mask of first rea if 2D !"
#	
#	for colname in colnames:
#		
#		mask = np.array(np.ma.getmaskarray(np.ma.array(cat[colname])), dtype=bool)
#		assert mask.ndim in [1, 2]
#		if mask.ndim == 2:
#			mask = mask[:,0] # Just get the first realization..
#			
#		assert mask.ndim == 1
#		assert mask.size == len(cat)
#		masklist.append(mask)
#	
#	# We now group all the masks for all these columns.
#	masks = np.column_stack(masklist)
#	
#	# This is a 2D boolean array. Now we log some details about how many points are masked in each column.
#	for (i, colname) in enumerate(colnames):
#		mask = masks[:,i]
#		assert len(mask) == len(cat)
#		nbad = np.sum(mask)
#		logger.info("Column %20s: %5i (%5.2f %%) of the %i entries are masked" \
#			% ("'"+colname+"'", nbad, 100.0 * float(nbad) / float(len(cat)), len(cat)))
#	
#	# Now we combine the masks:
#	combimask = np.logical_not(np.sum(masks, axis=1).astype(bool)) # So "True" means "keep this".
#	assert combimask.size == len(cat)
#	ngood = np.sum(combimask)
#	nbad = combimask.size - ngood
#	logger.info("Combination: %i out of %i (%.2f %%) rows have masked values and will be disregarded" \
#		% (nbad, combimask.size, 100.0 * float(nbad) / float(combimask.size)))
#	
#	# We disregard the masked rows:
#	nomaskcat = cat[combimask] # Only works as combimask is a numpy array ! It would do something else with a list !
#	# Wow, this is extremely SLOW !
#	# Note that everything so far also works for columns which are **not** masked. They will remain maskless.
#	
#	# More asserts:
#	assert len(nomaskcat) == ngood
#	for colname in colnames:
#		if hasattr(nomaskcat[colname], "mask"): # We make this test only if the column is masked
#			#assert np.all(np.logical_not(nomaskcat[colname].mask)) == True # Tests that all values are unmasked.
#			pass
#	
#	if not keep_all_columns:
#		nomaskcat.keep_columns(colnames)
#		# Moving this to before the slow "cat[combimask]" seems to not speedup this function -- strange ?
#	
#	return nomaskcat
#







"""
Functions to group and summarize measurements accross multiple realizations of simulations.

"""
import os
import sys
import glob
import re
import astropy
import numpy as np

from .. import tools

import logging
logger = logging.getLogger(__name__)



def simmeasdict(measdir, simparams):
	"""
	Function to help you explore available measurements of simulations for a given measdir and simparams.
	So this function is here to "glob" the random file names for you.
	
	:param measdir:
	:param simparams: 
	
	For this I use a regular expression, to avoid making exagerated assumptions about these filenames.
	I return a dict whose keys are the simulated catalog names, and the corresponding entries
	are lists of filenames of the pkls with the measurements on the different realizations for each catalog. 
	
	An example should clarify... here is the dict that I return::
		
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
	
	incatfilepaths = sorted(glob.glob(os.path.join(measdir, simparams.name, "*_meascat.pkl")))
	basenames = map(os.path.basename, incatfilepaths)

	# Here is how they look: 20141020T141239_9UhtkX_0_galimg_meascat.pkl
	# We get a unique list of the catalog names, using regular expressions
	
	p = re.compile("(\w*_\w*)_(\d*)_galimg_meascat.pkl")
	
	matches = [p.match(basename) for basename in basenames]
	if None in matches:
		raise RuntimeError("There are unexpected files in '%s'" % (measdir))
		
		
	namereatuples = [(match.group(0), match.group(1), match.group(2)) for match in matches]
	# This gives (full file name, catname, realization number)
	
	catnames = sorted(list(set([namereatuple[1] for namereatuple in namereatuples])))
	
	out = {}
	for catname in catnames:
		out[catname] = [namereatuple[0] for namereatuple in namereatuples if namereatuple[1] == catname]
	
	logger.info("Found %i catalogs, and %i realizations (%.1f per catalog, on average)" %
		(len(catnames), len(namereatuples), float(len(namereatuples))/float(len(catnames))))
	
	return out




def group(incats, colstogroup=None, colstoremove=None, removereas=True):
	"""
	This function "horizontally" merges some columns of input catalogs having the same columns by "hstacking" them.
	Then, for each colname in colstogroup, the function computes new "colname_mean" and "colname_std" columns.
	 
	:param incats: list of catalogs (astropy tables) that all have identical order and columns (will check this).
	:param colstogroup: the column names I should group, that is the columns that differ from incat to incat.
	:param colstoremove: any column names I should simply discard
	:param removereas: if True, I will not keep the individual realization columns in the output table. 
	
	The function tests that **any column which is not in colstogroup or colstoremove is indeed IDENTICAL among the incats**.
	It could be that this leads to perfomance issues one day, but in the meantime it should make things quite safe.
	"""
	if colstogroup == None:
		colstogroup = []
	if colstoremove == None:
		colstoremove = [] 

	colnames = incats[0].colnames
	for incat in incats:
		if incat.colnames != colnames:
			raise RuntimeError("Your input catalogs do not have the same columns: \n\n %s \n\n is not \n\n %s"
				% (incat.colnames, colnames))

	for coltogroup in colstogroup:
		if coltogroup not in colnames:
			raise RuntimeError("The column '%s' which I should group is not present in the catalog" % coltogroup)
		if coltogroup in colstoremove:
			raise RuntimeError("I cannot both group and remove column '%s' " % coltogroup)


	# We make a list of the column names that should stay unaffected:
	fixedcolnames = [colname for colname in colnames if (colname not in colstogroup) and (colname not in colstoremove)]
	
	# We will take those columns from the first incat (and test just below that this choice doesn't matter)
	outcat = incats[0][fixedcolnames] # This makes a copy
	
	# We test that the columns of these fixedcolnames are the same for the different incats !
	for incat in incats:
		if not np.all(incat[fixedcolnames] == outcat):
			raise RuntimeError("Something is fishy, some columns are not identical among %s. Add them to colstoremove." % outcat.colnames)
	
	
	# Now we prepare tables containing *only* the colstogroup:
	togroupincats = [incat[colstogroup] for incat in incats]
	
	# We prepare some "suffixes" for these columns. For this we do NOT reuse the int from the filename
	# Instead we just make a new integer range.
	incat_names = ["%i" % (i) for i in range(len(togroupincats))]
	
	# We use join to create all these new columns with the suffixes in their names
	togroupoutcat = astropy.table.hstack(togroupincats, join_type="exact",
		table_names=incat_names, uniq_col_name="{col_name}_{table_name}", metadata_conflicts="error")
	
	# For each coltogroup, we compute some statistics
	for coltogroup in colstogroup:
		
		suffixedcolnames = ["%s_%s" % (coltogroup, incat_name) for incat_name in incat_names]
		
		# It seems that we have to build the numpy array column by column
		numpycolumns = [np.array(togroupoutcat[suffixedcolname]) for suffixedcolname in suffixedcolnames]
		array = np.array(numpycolumns)
		
		meancolname = "%s_%s" % (coltogroup, "mean")
		togroupoutcat[meancolname] = np.mean(array, axis=0)
				
		stdcolname = "%s_%s" % (coltogroup, "std")	
		togroupoutcat[stdcolname] = np.std(array, axis=0)
		
		if removereas:
			togroupoutcat.remove_columns(suffixedcolnames)
		
	
	return togroupoutcat



def onsims(measdir, simparams, **kwargs):
	"""
	Top-level function to average measurements obtained with :func:`megalut.meas.run.onsims`
	
	I explore the files in your measdir, and will work on one catalog after the other.
	"""
	
	# We use the above function to find what we have:
	catdict = simmeasdict(measdir, simparams)
	
	# We iterate over one simulated catalog after the other.
	for (catname, meascatfilepaths) in catdict.items():
		
		logger.debug("Reading all meascats for catalog %s" % (catname))
		
		meascats = [tools.io.readpickle(os.path.join(measdir, simparams.name, meascatfilepath)) for meascatfilepath in meascatfilepaths]
		
		#print meascats[0].colnames
		
		#meascats[0].remove_column("adamom_flux")
		
		grouped = group(meascats, **kwargs)
	
		print grouped.colnames
	
		exit()
		
	# And finally we stack all these catalogs "vertically", to get a single one
	
	



#	This was for multidimensional arrays, but is not implemented : a simple hstack seems better
#
#def group(incats, colstogroup, colstoremove=None):
#	"""
#	I "merge" input catalogs by turning some scalar columns from different input catalogs
#	into single multidimensional columns in the output catalog. 
#	
#	:param incats: list of catalogs (astropy tables) that all have identical order and columns
#	:param colstogroup: the column names I should group
#	:param colstoremove: the column names I should discard
#	
#	"""
#
#	if colstoremove == None:
#		colstoremove = [] 
#
#	colnames = incats[0].colnames
#	for incat in incats:
#		if incat.colnames != colnames:
#			raise RuntimeError("Your input catalogs do not have the same columns: \n\n %s \n\n is not \n\n %s"
#				% (incat.colnames, colnames))
#
#	for coltogroup in colstogroup:
#		if coltogroup not in colnames:
#			raise RuntimeError("The column '%s' is not present in the catalog" % coltogroup)
#		if coltogroup in colstoremove:
#			raise RuntimeError("I cannot both group and remove column '%s' " % coltogroup)
#
#
#	colnamestokeep = [colname for colname in colnames if (colname not in colstogroup) and (colname not in colstoremove)]
#	
#	outcat = incats[0][colnamestokeep] # This makes a copy
#	
#	return outcat





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

	


#def onsims(measdir, simparams):
#	"""
#	Top-level function to average measurements obtained with :func:`megalut.meas.run.onsims`
#	
#	I explore the files in your measdir, and will work on one catalog after the other.
#	"""
#	
#	
#	catdict = simmeasdict(measdir, simparams)
#	
#	for (catname, meascatfilepaths) in catdict.items():
#		
#		#print catname
#		meascats = [tools.io.readpickle(os.path.join(measdir, simparams.name, meascatfilepath)) for meascatfilepath in meascatfilepaths]
#		
#		#print meascats[0].colnames
#		
#		#meascats[0].remove_column("adamom_flux")
#		
#		grouped = group(meascats, ["adamom_flux"])
#	
#		print grouped.colnames
#	
#		exit()
#	
#	
#	"""
#	incatfilepaths = sorted(glob.glob(os.path.join(measdir, simparams.name, "*_galimg_meascat.pkl")))
#	
#	basenames = map(os.path.basename, incatfilepaths)
#	
#	# Here is how they look: 20141020T141239_9UhtkX_0_galimg_meascat.pkl
#	# We get a unique list of the catalog names, using regular expressions
#	
#	p = re.compile("\w*_\w*_\d*_)
#	
#	catnames = sorted(list(set([])))
#	"""
#	
#	"""
#	catnames = sorted(list(set([os.path.splitext(basename)[0][:]])))
#	
#	if len(incatfilepaths) == < 2:
#		raise RuntimeError("I could find only %i catalogs, I need more !")
#
#
#	for 
#	"""

	
	
	
	

"""
Functions to group and summarize measurements accross multiple realizations of simulations.

"""
import os
import sys
import glob
import re

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
	


#	Not implemented : a simple hstack seems better
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





class Operation():
	"""
	Class to hold the column name and the type of operation to perform
	"""
	
	def __init__(self, incolname, outcolname, optype="avg"):
		
		self.incolname = incolname
		self.outcolname = outcolname
		if optype not in ["avg"]:
			raise RuntimeError("Unknown optype")
		self.optype = optype
		
		
def general(incats, operations, idcolname="id"):
	"""
	
	:param incats: a list of input catalogs (astropy tables)	
	:param operations: a list of Operation objects defining what should be done
	
	:param idcolname: I use this column to cross-identify galaxies between the different catalogs
		Set this to None if you don't want me to check the ids, and just assume your catalogs are
		all sorted in the same way.
	
	:returns: an output catalog
	"""
	
	
	# Sort input catalogs using idcolname
	

	for operation in operations:
		
		pass
		

	


def onmeas(measdir, simparams):
	"""
	Top-level function to average measurements obtained with :func:`megalut.meas.run.onsims`
	
	I explore the files in your measdir, and will work on one catalog after the other.
	"""
	
	
	catdict = simmeasdict(measdir, simparams)
	
	for (catname, meascatfilepaths) in catdict.items():
		
		#print catname
		meascats = [tools.io.readpickle(os.path.join(measdir, simparams.name, meascatfilepath)) for meascatfilepath in meascatfilepaths]
		
		#print meascats[0].colnames
		
		#meascats[0].remove_column("adamom_flux")
		
		grouped = group(meascats, ["adamom_flux"])
	
		print grouped.colnames
	
		exit()
	
	
	"""
	incatfilepaths = sorted(glob.glob(os.path.join(measdir, simparams.name, "*_galimg_meascat.pkl")))
	
	basenames = map(os.path.basename, incatfilepaths)
	
	# Here is how they look: 20141020T141239_9UhtkX_0_galimg_meascat.pkl
	# We get a unique list of the catalog names, using regular expressions
	
	p = re.compile("\w*_\w*_\d*_)
	
	catnames = sorted(list(set([])))
	"""
	
	"""
	catnames = sorted(list(set([os.path.splitext(basename)[0][:]])))
	
	if len(incatfilepaths) == < 2:
		raise RuntimeError("I could find only %i catalogs, I need more !")


	for 
	"""

	
	
	
	

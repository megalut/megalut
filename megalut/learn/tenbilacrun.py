"""
This is a standalone wrapper for Tenbilac, featuring:

  - a simpler configuration, making it easy to explore, run and use different trainings
  - a no-brainer way to run several trainings one after the other (no multiprocessing, as tenbilac does this internally).


"""
import datetime
import numpy as np
import astropy
import copy

import os
from ConfigParser import SafeConfigParser
from .. import tools

import tenbilac

import logging
logger = logging.getLogger(__name__)




def train(catalog, conflist, workbasedir):
	"""
	Top-level function to train Tenbilacs with data from a MegaLUT catalog.
	Does not modify or return the input catalog, it really just trains.
	
	:param conflist: A list of tuples ("ada5g1.cfg", "sum55.cfg") of filepaths to the configuration files for the data selection and the machine learning.
		Tuples in this list are processed one after the other.
	:param workbasedir: A directory in which the trainings can be organized.
		I will create a subdirectory in there reflecting the configuration names.
	
	It returns a list of names of the Tenbilac workdirs (as long as conflist).
	This can be useful for example if you want to save plots, catalogs or (self-)predictions in there automatically after the training.	
	"""
	starttime = datetime.datetime.now()
	logger.info("Starting the training of {} MLs...".format(len(conflist)))
	
	trainworkdirs = []
	for (dataconfpath, toolconfpath) in conflist:
		
		# We read in the configurations
		dataconfig = readconfig(dataconfpath) # The data config (what to train usign which features)
		toolconfig = readconfig(toolconfpath) # The Tenbilac config
		confname = dataconfig.get("setup", "name") + "_" + toolconfig.get("setup", "name") # Will be passed to Tenbilac
		trainworkdir = os.path.join(workbasedir, confname) # We will pass this to Tenbilac
		trainworkdirs.append(confname)
		
		# We get the config in form of python lists:
		inputlabels = list(eval(dataconfig.get("data", "inputlabels")))
		auxinputlabels = list(eval(dataconfig.get("data", "auxinputlabels")))
		targetlabels = list(eval(dataconfig.get("data", "targetlabels")))
		
		# Preparing the inputs
		inputsdata = get3Ddata(catalog, inputlabels)
		if len(auxinputlabels) != 0:
			logger.info("We have auxinputs")
			auxinputsdata = get3Ddata(catalog, auxinputlabels)
		else:
			logger.info("No auxinputs")
			auxinputsdata = None
		
		# Preparing the targets
		for colname in targetlabels:
			if not np.all(np.logical_not(np.ma.getmaskarray(catalog[colname]))): # No element should be masked.
				raise RuntimeError("Targets should not be masked, but '{}' is!".format(colname))
		targetsdata = np.column_stack([np.array(catalog[colname]) for colname in targetlabels]).transpose()
		assert inputsdata.shape[2] == targetsdata.shape[1] # Number of cases should match
		if auxinputsdata is not None:
			assert auxinputsdata.shape[2] == targetsdata.shape[1] #  Number of cases must match!
				# note that these tests are repeated withing tenbilac, of course.			

		
		# And calling Tenbilac
		tblconfiglist = [("setup", "workdir", trainworkdir), ("setup", "name", confname)]
		ten = tenbilac.com.Tenbilac(toolconfpath, tblconfiglist)
		
		ten.train(inputsdata, targetsdata, inputlabels, targetlabels, auxinputs=auxinputsdata)
		
	
		
	endtime = datetime.datetime.now()
	logger.info("Done, the total time for training the %i MLs was %s" % (len(conflist), str(endtime - starttime)))
	
	return trainworkdirs


def confnames(conflist):
	"""
	Returns a list of names for the conflist items, which can be used as directories.
	This is exactly what train also returns.
	"""
	output = []
	for (dataconfpath, toolconfpath) in conflist:
		# We read in the configurations
		dataconfig = readconfig(dataconfpath) # The data config (what to train usign which features)
		toolconfig = readconfig(toolconfpath) # The Tenbilac config
		confname = dataconfig.get("setup", "name") + "_" + toolconfig.get("setup", "name")
		output.append(confname)
	return output



def predict(catalog, conflist, workbasedir=None):
	"""
	Top level-function to make predictions. The only "tricky" thing here is that it returns a single catalog with all the new columns.
	This catalog is built progressively: the second machine in your configlist could potentially use predictions from the first one as inputs.
	
	The input catalog is not modified.
	
	If any feature values of your catalog are masked, the corresponding rows in the output catalog will not be predicted,
	and the prediction columns will get masked accordingly.
	
	Same arguments as for train, but conflist can *alternatively* consist of tuples ("ada5g1.cfg", "/path/to/tenbilac-workdir/to/use").
		If the tenbilac configuration is given as a directory, then this directory is used to make predictions, intead of the
		combination of workbasedir and the configuration names as done during the training.
		The argument workbasedir is ignored, in this case. This feature makes it much simpler and safer to write standalone scripts 
		that apply a bunch of trained Tenbilacs to data.
	
	"""
	starttime = datetime.datetime.now()
	logger.info("Starting predictions from {} MLs...".format(len(conflist)))
	
	outcat = astropy.table.Table(copy.deepcopy(catalog), masked=True)
	
	for (dataconfpath, toolconfpath) in conflist:
		
		# We read in the configurations, as for the training, to get the Tenbilac workdir to use.
		dataconfig = readconfig(dataconfpath)
		if os.path.isfile(toolconfpath):
			toolconfig = readconfig(toolconfpath)
			trainworkdir = os.path.join(workbasedir, dataconfig.get("setup", "name") + "_" + toolconfig.get("setup", "name"))
		elif os.path.isdir(toolconfpath):
			# Then we don't have to read this now. Tenbilac will take care of it.
			trainworkdir = toolconfpath
		else:
			raise RuntimeError("Tenbilac config '{}' does not exist.".format(toolconfpath))
		logger.info("Preparing for predictions usign the Tenbilac workdir '{}'...".format(trainworkdir))
		
		# We get the required data config in form of python lists:
		inputlabels = list(eval(dataconfig.get("data", "inputlabels")))
		predlabels = list(eval(dataconfig.get("data", "predlabels")))
		
		# Check that the predictions do not yet exist
		for predlabel in predlabels:
			if predlabel in catalog.colnames:
				raise RuntimeError("The predlabel '%s' already exists in the catalog!" % predlabel)
		
		# Preparing the inputs
		inputsdata = get3Ddata(outcat, inputlabels)
		
		# And calling Tenbilac
		tblconfiglist = [("setup", "workdir", trainworkdir)]
		ten = tenbilac.com.Tenbilac(toolconfpath, tblconfiglist)
		
		preddata = ten.predict(inputsdata)
		
		# We add this to the outcat.
		# An explicit loop, to highlight that we care very much about the order (to get targetlabels right)
			
		for (i, predlabel) in enumerate(predlabels):	
			logger.info("Adding predictions '{}' to catalog...".format(predlabel))
			data = preddata[:,i,:].transpose()
 			assert data.ndim == 2 # Indeed this is now always 2D.
 			if data.shape[1] == 1: # If we have only one realization, just make it a 1D numpy array.
 				data = data.reshape((data.size))
 				assert data.ndim == 1
						
 			newcol = astropy.table.MaskedColumn(data=data, name=predlabel)
 			outcat.add_column(newcol)
			
	endtime = datetime.datetime.now()
	logger.info("Done, the total time for the predictions was {}".format(str(endtime - starttime)))

	return outcat


def readconfig(configpath):
	"""
	Reads in a config file
	"""
	config = SafeConfigParser(allow_no_value=True)
	
	if not os.path.exists(configpath):
		raise RuntimeError("Config file '{}' does not exist!".format(configpath))
	logger.debug("Reading config from '{}'...".format(configpath))
	config.read(configpath)
	
	name = config.get("setup", "name") 
	if name is None or len(name.strip()) == 0: # if the ":" is missing as well, confirparser reads None
		# Then we use the filename
		config.set("setup", "name", os.path.splitext(os.path.basename(configpath))[0])
	logger.info("Read config '{}' from file '{}'.".format(config.get("setup", "name"), configpath))	
	
	return config
	

def get3Ddata(catalog, colnames):
	"""
	Function to build a 3D numpy array (typically for Tenbilac input) from some columns of an astropy catalog.
	The point is to ensure that all columns get the same shape.
	
	The 3D output array has shape (realization, feature, case).
	"""
	
	if len(colnames) == 0:
		raise RuntimeError("No colnames to get data from!")
	
	# Check for exotic catalogs (do they even exist ?)
	for colname in colnames:
		if not catalog[colname].ndim in [1, 2]:
			raise RuntimeError("Can only work with 1D or 2D columns")
	
	# Let's check the depths of the 2D colums to see what size we need.
	nreas = list(set([catalog[colname].shape[1] for colname in colnames if catalog[colname].ndim == 2]))
	#logger.info("We have the following nreas different from one in there: {}".format(nreas))
	if len(nreas) > 1:
		raise RuntimeError("The columns have incompatible depths!")

	if len(nreas) == 0:
		nrea = 1
		logger.info("For each column, only one realization is available.")
		
	else:
		nrea = nreas[0]
		logger.info("Extracting data from {0} realizations...".format(nrea))
		nrea = nreas[0]
	
	if "ngroup" in catalog.meta:
		if nrea != catalog.meta["ngroup"]:
			raise RuntimeError("Something very fishy: depth is not ngroup!")

	# And now we get the data:
	
	readycols = []
	for colname in colnames:
				
		col = np.ma.array(catalog[colname])
				
		if col.ndim == 2:
			pass
			
		elif col.ndim == 1:
			# This column has only one realization, and we have to "duplicate" it nrea times...
			col = np.tile(col, (nrea, 1)).transpose()
					
		else:
			raise RuntimeError("Weird column dimension")
								
		readycols.append(col)
		
	outarray = np.rollaxis(np.ma.array(readycols), 2)
	
	assert outarray.ndim == 3
	assert outarray.shape[1] == len(colnames)

	return outarray

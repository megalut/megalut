"""
A module to connect the shape measurement stuff (astropy.table catalogs...) to the machine learning
(ml) wrappers.
It also takes care of masked columns, so that the underlying ml wrappers do not have to deal with
masked arrays (except for Tenbilac, as Tenbilac uses masked arrays).
"""

import numpy as np
from datetime import datetime
import os

import skynetwrapper
import fannwrapper
import tenbilacwrapper

#import ffnetwrapper
#import pybrainwrapper
#import minilut

import astropy.table
import copy

import logging
logger = logging.getLogger(__name__)


class MLParams:
	"""
	A container for the general parameters describing the machine learning:
	what inputs should I use to predict what targets ?
	"""
	
	def __init__(self, name, inputs, targets, predictions, auxinputs=None):
		"""
		inputs, targets, and predictions are lists of strings, with the names of the columns of
		the catalog to use. Idem for auxinputs, which is optional.

		:param name: pick a short string describing these machine learning params.
			It will be used within filenames to store ML data.
		:param inputs: the list of column names to be used as input, i.e. "inputs", for
			the machine learning
		:param targets: the list of column names that the machine should aim at (that is, the "truth")
		:param predictions: the corresponding list of column names where predictions should be written,
			in the returned catalog.
		:param auxinputs: further inputs, for special cost functions (so far only used by Tenbilac).
		
		To give a minimal example, to predict ellipticity you could use something like::
			
			name = "simpleshear"
			inputs = ["mes_g1", "mes_g2", "mes_size", "mes_flux"]
			targets = ["tru_g1", "tru_g2"]
			predictions = ["pre_g1", "pre_g2"]
		
		"""
		
		self.name = name
		self.inputs = inputs
		self.targets = targets
		self.predictions = predictions
		
		if auxinputs is None:
			auxinputs = []
		
		self.auxinputs = auxinputs

		# This is no longer the case with Tenbilac:
		#assert len(self.targets) == len(self.predictions)
		

	def __str__(self):
		txt = "ML parameters \"%s\":\n" % (self.name) + \
			"Inputs:    %s\n" % (", ".join(self.inputs)) + \
			"Targets:      %s\n" % (", ".join(self.targets)) + \
			"Predictions: %s\n" % (", ".join(self.predictions)) + \
			"Auxinputs: %s" % (", ".join(self.auxinputs))
		return txt


class ML:
	"""
	This is a class that will hopefully nicely wrap any supervised machine learning regression code.
	
	This class has two key methods: train and predict. These methods call the "train"
	and "predict" methods of the underlying machine learning wrappers.
	For this to work, any machine learning wrapper has to implement methods with such names.
	"""

	def __init__(self, mlparams, toolparams, workbasedir = "."):
		"""
		:param mlparams: an MLParams object, describing *what* to learn.
		:param toolparams: this describes *how* to learn. For instance a FANNParams object, if you
			want to use FANN.
		:param workbasedir: path to a directory in which the machine parameters and any other
			intermediary or log files can be stored.
			Within this directroy, the training method will create a subdirectory using the
			mlparams.name and toolparams.name. So you can very well give the **same workbasedir**
			to different ML objects.
			If not specified (default), the current working directory will be used as workbasedir.
		"""
		
		self.mlparams = mlparams
		self.toolparams = toolparams
		self.workbasedir = workbasedir
		
		self.toolname = None # gets set below
		self.workdir = None # gets set below, depending on the tool to be used
		
		if isinstance(self.toolparams, fannwrapper.FANNParams):
			self.toolname = "FANN"
			self._set_workdir()
			self.tool = fannwrapper.FANNWrapper(self.toolparams, workdir=self.workdir)
		
		elif isinstance(self.toolparams, skynetwrapper.SkyNetParams):
			self.toolname = "SkyNet"
			self._set_workdir()
			self.tool = skynetwrapper.SkyNetWrapper(self.toolparams, workdir=self.workdir)
		elif isinstance(self.toolparams, tenbilacwrapper.TenbilacParams):
			self.toolname = "Tenbilac"
			self._set_workdir()
			self.tool = tenbilacwrapper.TenbilacWrapper(self.toolparams, workdir=self.workdir)
		
		else:
			raise RuntimeError("toolparams not recognized")
			# ["skynet", "ffnet", "pybrain", "fann", "minilut"]
		
	
	def __str__(self):
		"""
		A string describing an ML object, that will also be used as workdir name.
		"""
		return "ML_%s_%s_%s" % (self.toolname, self.mlparams.name, self.toolparams.name)
		
	
	def _set_workdir(self):
		self.workdir = os.path.join(self.workbasedir, str(self))
	

	def get_workdir(self):
		logger.warning("This will be removed: directly use ml.workdir")
		return self.workdir
		
	
	def looks_same(self, other):
		"""
		Compares self to another ML object, and returns True if the objects seem to describe the "same"
		machine learning, in terms of parameters. Otherwise it returns False.
		
		:param other: an other ML object to compare with
		
		In principle this method might be called __eq__ to overwrite the default equality comparion,
		but given that it is not trivial it seems safer to just define it as a stand-alone function.
		"""
		return self.mlparams.__dict__ == other.mlparams.__dict__ and \
			self.toolparams.__dict__ == other.toolparams.__dict__ and \
			self.workbasedir == other.workbasedir and \
			self.toolname == other.toolname and \
			self.workdir == other.workdir


	def train(self, catalog):
		"""
		Runs the training, by extracting the numbers from the catalog and feeding them
		into the "train" method of the ml tool.
		The main part is to translate the (masked) catalog columns into a single appropriate numpy array
		that serves as input to the wrappers.
		
		:param catalog: an input astropy table. Has to contain the inputs and the targets.
			It can well be masked. Only those rows for which all the required
			inputs and targets are unmasked will be used for the training.
			When using Tenbilac, masked realizations stay in!
		
		"""	
		starttime = datetime.now()
			
		logger.info("Training %s in %s..." % (str(self), self.workdir))
		logger.info(str(self.mlparams))
		logger.info(str(self.toolparams))
		
		
		# Now we extract the data from the catalog and prepare plain numpy arrays.
		# For FANN and SkyNet, we have to reject any masked stuff, and provide one "value" per feature.
		# For Tenbilac, things are different. We have to provide 3D input (realization, feature, galaxy)
		
		if isinstance(self.toolparams, tenbilacwrapper.TenbilacParams): # Tenbilac
			
			self.toolparams.ncpu = self.toolparams.commncpu
			
			logger.debug("Found a Tenbilac instance, to run on {:d} CPUs".format(self.toolparams.ncpu))
				
			inputsdata = get3Ddata(catalog, self.mlparams.inputs)
			
			if len(self.mlparams.auxinputs) != 0:
				auxinputsdata = get3Ddata(catalog, self.mlparams.auxinputs)
			else:
				auxinputsdata = None
			
			# Now we prepare the targets, in a similar way.
			# Change this so that it also works for masked targets? No, probably we never need this.
			for colname in self.mlparams.targets:
				if not np.all(np.logical_not(np.ma.getmaskarray(catalog[colname]))): # No element should be masked.
					raise RuntimeError("Targets should not be masked, but '{}' is!".format(colname))
					
			targetsdata = np.column_stack([np.array(catalog[colname]) for colname in \
				self.mlparams.targets]).transpose()
			
			assert inputsdata.shape[2] == targetsdata.shape[1] #  Number of cases must match!
			if auxinputsdata is not None:
				assert auxinputsdata.shape[2] == targetsdata.shape[1] #  Number of cases must match!
				# note that these tests are repeated withing tenbilac, of course.			

			# And we call the tool's train method:
			self.tool.train(inputs=inputsdata, targets=targetsdata, auxinputs=auxinputsdata,
				inputnames=self.mlparams.inputs,
				targetnames=self.mlparams.targets
				)
	

		
		else: # FANN or SkyNet etc
		
			if len(self.mlparams.auxinputs) != 0:
				raise RuntimeError("Something fishy, auxinputs cannot be used with FANN or SkyNet.")
		
			# We can only use a row for training if all its inputs and all targets are unmasked.
			# So we build such a "combined mask", to extract these rows.
			# We do not want this to fail on unmasked astropy tables, and so to make it easy
			# we convert everything to masked arrays.
			
			
			for colname in self.mlparams.inputs + self.mlparams.targets:
				assert catalog[colname].ndim == 1 # This code was not desinged for 2D columns.
			
			masks = np.column_stack([
				np.array(np.ma.getmaskarray(np.ma.array(catalog[colname])), dtype=bool) \
				for colname in self.mlparams.inputs + self.mlparams.targets])
			combimask = np.sum(masks, axis=1).astype(bool)
			assert combimask.size == len(catalog)
		
			logger.info("%i out of %i (%.2f %%) rows have masked inputs or targets and will not be used" \
				% (np.sum(combimask), combimask.size, 100.0 * float(np.sum(combimask)) / float(combimask.size)))
		
			# Now we turn the relevant rows and columns of the catalog into unmasked 2D numpy arrays.
			# There are several ways of turning astropy.tables into plain numpy arrays.
			# The shortest is np.array(table...)
			# I use the following one, as I find it the most explicit (in terms of respecting
			# the order of inputs and targets).
			# We could add dtype control, but the automatic way should work fine.
		
			inputsdata = np.column_stack([np.array(catalog[colname])[np.logical_not(combimask)] for colname in \
				self.mlparams.inputs])	
			targetsdata = np.column_stack([np.array(catalog[colname])[np.logical_not(combimask)] for colname in \
				self.mlparams.targets])
		
			assert inputsdata.shape[0] == np.sum(np.logical_not(combimask)) # Number of good (unmasked) rows
			assert targetsdata.shape[0] == np.sum(np.logical_not(combimask)) # Number of good (unmasked) rows
		
		
		
		
			# And we call the tool's train method:
			self.tool.train(features=inputsdata, labels=targetsdata)
		
		endtime = datetime.now()
		logger.info("Done! This training took %s" % (str(endtime - starttime)))
		


	def predict(self, catalog, **kwargs):
		"""
		Computes the prediction(s) based on the inputs in the given catalog.
		Of course it will return a new astropy.table to which the new "predictions" columns are added,
		instead of changing your catalog in place.
		If any feature values of your catalog are masked, the corresponding rows will not be predicted,
		and the predictions columns will get masked accordingly.
		
		"""
		logger.info("Predicting %s with %s using inputs %s..." % (self.mlparams.predictions, str(self), self.mlparams.inputs))
		
		# First let's check that the predictions do not yet exist
		for predlabel in self.mlparams.predictions:
			if predlabel in catalog.colnames:
				raise RuntimeError("The predlabel '%s' already exists in the catalog, refusing to overwrite" % predlabel)
		
		
		# From here on, things depend on the ML algo (as Tenbilac uses 2D columns...)
		if isinstance(self.toolparams, tenbilacwrapper.TenbilacParams): # Tenbilac

			# We do not care about removing masks by hand here, as Tenbilac can deal with this.
			
			inputsdata = get3Ddata(catalog, self.mlparams.inputs)
			preddata = self.tool.predict(inputs=inputsdata)
			
			# This is an appropriately masked 3D numpy array
			
			# We now add this preddata to the output catalog.
			# We'll work on and return a **masked** copy of the input catalog.
			# Probably the input catalog was already masked anyway.
			
			outcat = astropy.table.Table(copy.deepcopy(catalog), masked=True)
			# ... to which we add the preddata.
			# An explicit loop, to highlight that we care very much about the order (to get targets right)
			
			for (i, predlabel) in enumerate(self.mlparams.predictions):
				
				# If there is a function to treat the catalogue, let's do it now...
				fun = kwargs['fun']
				#nreas = preddata.shape[1]
				if not fun is None:
					treatedpred = fun(preddata[:,:,i,:], axis=0).transpose()
					treatedpred = treat_col(treatedpred)
					newcol = astropy.table.MaskedColumn(data=treatedpred, name=predlabel)
					outcat.add_column(newcol)	
					
				# Another explicit loop to go through all the members of the committee
				for j in range(self.tool.params.nmembers):
					data=preddata[j,:,i,:].transpose()
					data = treat_col(data)

					# If there is only one net in the committee, let's make no fuss about the colname
					colname = predlabel
					if self.tool.params.nmembers > 1:
						colname += "_{:03d}".format(j)						
					
					newcol = astropy.table.MaskedColumn(data=data, name=colname)
					outcat.add_column(newcol)	
				
					
		else: # FANN or SkyNet etc:	
		
			# We rather manually build a mask for the inputs. A row is masked whenever one or more inputs are masked.
			inputsmask = np.column_stack([
				np.array(np.ma.getmaskarray(np.ma.array(catalog[feature])), dtype=bool) \
				for feature in self.mlparams.inputs])
			allinputsmask = np.sum(inputsmask, axis=1).astype(bool)
			assert allinputsmask.size == len(catalog)
		
			logger.info("%i out of %i (%.2f %%) rows have masked inputs and will not be predicted" \
				% (np.sum(allinputsmask), allinputsmask.size, 100.0 * float(np.sum(allinputsmask)) / float(allinputsmask.size)))
			
			# Now we get the array of unmasked inputs:
			inputsdata = np.column_stack([np.array(catalog[colname])[np.logical_not(allinputsmask)] for colname in self.mlparams.inputs])
			assert inputsdata.shape[0] == np.sum(np.logical_not(allinputsmask)) # Number of good (unmasked) rows
			assert inputsdata.shape[1] == len(self.mlparams.inputs) # Number of inputs
			
			# We can run the prediction tool, it doesn't have to worry about any masks:
			preddata = self.tool.predict(features=inputsdata)
			
			# Let's check that the output looks good:
			assert preddata.shape[0] == np.sum(np.logical_not(allinputsmask)) # Number of good (unmasked) rows
			assert preddata.shape[1] == len(self.mlparams.predictions) # Number of predictions

			# Finally, we build a catalog containing the predicted data.
			# We'll work on and return a **masked** copy of the input catalog
			# Probably the input catalog was already masked anyway.
			outcat = astropy.table.Table(copy.deepcopy(catalog), masked=True)
			
			# ... to which we add masked columns.
			# An explicit loop, to highlight that we care very much about the order (to get targets right).
			for (i, predlabel) in enumerate(self.mlparams.predictions):
			
				newcoldata = np.ma.masked_all(len(outcat)) # All entries masked
				newcoldata[np.logical_not(allinputsmask)] = preddata[:,i] # Automatically unmasks entries
				newcol = astropy.table.MaskedColumn(data=newcoldata, name=predlabel) 
				assert len(newcol) == len(outcat) # OK, hard to imagine how this can fail
				assert np.all(newcol.mask == allinputsmask) # This checks that the newcol was correctly created
				
				outcat.add_column(newcol)

	
	
		return outcat
	
		
def treat_col(data):
	"""
	Helper function for the treatment of a tenbilac output
	"""
	assert data.ndim == 2 # Indeed this is now always 2D.
	if data.shape[1] == 1: # If we have only one realization, just make it a 1D numpy array.
		data = data.reshape((data.size))
		assert data.ndim == 1	
	
	return data

def get3Ddata(catalog, colnames):
	"""
	Function to build a 3D numpy array (typically for Tenbilac input) from some columns of an astropy catalog.
	The point is to ensure that all columns get the same shape.
	
	The 3D output array has shape (realization, feature, galaxy).

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

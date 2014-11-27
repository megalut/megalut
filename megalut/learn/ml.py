"""
A module to connect the shape measurement stuff (astropy.table catalogs...) to the machine learning
(ml) wrappers.
"""

import numpy as np
from datetime import datetime
import os

import skynetwrapper
import fannwrapper
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
	what features should I use to predict what labels ?
	Features, labels, and predlabels are lists of strings, with the names of the columns of
	the catalog to use.

	:param name: pick a short string describing these machine learning params.
	             It will be used within filenames to store ML data.
	:param features: the list of column names to be used as input, i.e. "features", for
	             the machine learning
	:param labels: the list of column names that I should learn to predict (that is, the "truth")
	:param predlabels: the corresponding list of column names where I should write my predictions
		
	To give a minimal example, to predict shear you could use something like:
	
	>>> features = ["mes_g1", "mes_g2", "mes_size", "mes_flux"],
	>>> labels = ["tru_g1", "tru_g2"]
	>>> predlabels = ["pre_g1", "pre_g2"]
	
	"""
	
	def __init__(self, name, features, labels, predlabels):
		"""
		Text written here does not show up in the doc with the default sphinx apidoc params,
		as __init__ is private.
		One reason why we'll replace apidoc...
		"""
		
		self.name = name
		self.features = features
		self.labels = labels
		self.predlabels = predlabels

		assert len(self.labels) == len(self.predlabels)
		

	def __str__(self):
		txt = "ML parameters \"%s\":\n" % (self.name) + \
			"Features:    %s\n" % (", ".join(self.features)) + \
			"Labels:      %s\n" % (", ".join(self.labels)) + \
			"Predictions: %s" % (", ".join(self.predlabels))
		return txt




class ML:
	"""
	This is a class that will hopefully nicely wrap any machine learning regression code.
	
	:param mlparams: an MLParams object, describing *what* to learn.
	:param toolparams: this describes *how* to learn. For instance a FANNParams object, if you
	                 want to use FANN.
	:param workbasedir: path to a directory in which I should keep what I've learned.
	                 Within this directroy, I will create subdirectories using the
			 mlparams.name and toolparams.name. If not specified, I use the current
			 directory as workbasedir.

	This class has two key methods: train and predict. These methods directly call the train
	and predict methods of the underlying machine learning wrappers.
	So any machine learning wrapper has to implement such methods.
	
	"""

	def __init__(self, mlparams, toolparams, workbasedir = "."):
		
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
			self.tool = skynet.SkyNetWrapper(self.toolparams, workdir=self.workdir)
		
		else:
			raise RuntimeError("toolparams not recognized")
			# ["skynet", "ffnet", "pybrain", "fann", "minilut"]
		
	
	def __str__(self):
		"""
		A string describing an ML object, that will also be used as workdir.
		"""
		return "ML_%s_%s_%s" % (self.toolname, self.mlparams.name, self.toolparams.name)
		
	
	def _set_workdir(self):
		self.workdir = os.path.join(self.workbasedir, str(self))
	

	def get_workdir(self):
		logger.warning("This will be removed: directly use ml.workdir")
		return self.workdir
		
	
	def looks_same(self, other):
		"""
		Compares self to another ML object, and returns True if the objects seem to describe the same machine learning,
		otherwise False.
		
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
		
		:param catalog: an input astropy table. Has to contain the features and the labels.
			It can well be masked. Only those rows for which all the required
			features and labels are unmasked will be used for the training.
		
		"""	
		starttime = datetime.now()
			
		logger.info("Training %s (%s, %s) with %i galaxies in %s..." % \
				    (self.toolname, self.mlparams.name, self.toolparams.name,
				     len(catalog), self.workdir))
		logger.info(str(self.mlparams))
		logger.info(str(self.toolparams))
		
		
		# Now we turn the relevant columns of catalog into 2D numpy arrays.
		# There are several ways of turning astropy.tables into plain numpy arrays.
		# The shortest is np.array(table...)
		#featurescat = catalog[self.mlparams.features]
		#featuresdata = np.array(featurescat).view((float, len(featurescat.dtype.names)))
		
		# I use the following one, as I find it the most explicit (in terms of respecting
		# the order of features and labels)
		# We could add dtype control, but the automatic way should work fine.
		
		featuresdata = np.column_stack([np.array(catalog[colname]) for colname in \
							self.mlparams.features])
		labelsdata = np.column_stack([np.array(catalog[colname]) for colname in \
						      self.mlparams.labels])
		
		assert featuresdata.shape[0] == labelsdata.shape[0]
		
		self.tool.train(features=featuresdata, labels=labelsdata)
	
		endtime = datetime.now()
		logger.info("Done! This training took %s" % (str(endtime - starttime)))


	

	def predict(self, catalog):
		"""
		Computes the prediction(s) based on the features in the given catalog.
		Of course it will return a new astropy.table to which the new "predlabels" columns are added,
		instead of changing your catalog in place.
		If any feature values of your catalog are masked, the corresponding rows will not be predicted,
		and the predlabels columns will get masked accordingly.
		
		"""
		
		# First let's check that the predlabels do not yet exist
		for colname in self.mlparams.predlabels:
			if colname in catalog.colnames:
				raise RuntimeError("The predlabel '%s' already exists in the catalog" % colname)
		
		logger.info("Predicting %i galaxies using the %s (%s, %s) in %s..." % \
				    (len(catalog), self.toolname, self.mlparams.name,
				     self.toolparams.name, self.workdir))
		
		# Again, we get the features
		featuresdata = np.column_stack([np.array(catalog[colname]) for colname in \
							self.mlparams.features])

		preddata = self.tool.predict(features=featuresdata)
		
		assert preddata.shape[0] == len(catalog) # Number of galaxies has to match
		assert preddata.shape[1] == len(self.mlparams.predlabels) # Number of predlabels
                                                                          # has to match
		
		# We prepare the output catalog
		output = copy.deepcopy(catalog)
		
		# An explicit loop, to highlight that we care very much about the order.
		# Note that this might be slow for large tables anyway (adding columns generates
		# copies in memory)
		for (i, predlabel) in enumerate(self.mlparams.predlabels):
			output.add_column(astropy.table.Column(name = predlabel,
							       data = preddata[:,i]))
		return output
	
		


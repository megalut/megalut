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
		
		if isinstance(self.toolparams, fannwrapper.FANNParams):
			self.toolname = "FANN"
			self.workdir = os.path.join(workbasedir,
						    "ML_%s_%s_%s" % (self.toolname,
								     self.mlparams.name,
								     self.toolparams.name))
			self.tool = fannwrapper.FANNWrapper(self.toolparams, workdir=self.workdir)
		elif isinstance(self.toolparams, skynetwrapper.SkyNetParams):
			self.toolname = "SkyNet"
			self.workdir = os.path.join(workbasedir,
						    "ML_%s_%s_%s" % (self.toolname,
								     self.mlparams.name,
								     self.toolparams.name))
			self.tool = skynet.SkyNetWrapper(self.toolparams, workdir=self.workdir)
		else:
			raise RuntimeError()
			# ["skynet", "ffnet", "pybrain", "fann", "minilut"]
		
		
		if os.path.exists(self.workdir):
			logger.warning("ML workdir %s already exists, I might overwrite stuff !" % \
					       self.workdir)
		
	def train(self, catalog):
		"""
		Runs the training, by extracting the numbers from the catalog and feeding them
		into the "train" method of the ml tool.
		
		:param catalog: an input astropy table. Has to contain the features and the labels.
		
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
		Same idea as for train, but now with the prediction.
		Of course I will return a new astropy.table to which I add the "predlabels" columns,
		instead of changing your catalog in place !
		"""
		
		# First let's check that the predlabels do not yet exist
		for colname in self.mlparams.predlabels:
			assert colname not in catalog.colnames
		
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
	
	def get_fnames(self):
		return [self.tool.workdir, self.tool.get_fnames()]
		


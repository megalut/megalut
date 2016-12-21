"""
Wrapper around Tenbilac

https://github.com/mtewes/tenbilac

There is not that much to do here, as tenbilac directly uses numpy arrays natively.

"""


import os

import tenbilac

import logging
logger = logging.getLogger(__name__)


class TenbilacParams:
	"""
	For Tenbilac, there is nothing but a path in here.
	We keep the structure for consistency with other ML-packages.
	"""
	
	def __init__(self, configpath, name=None):
		"""
		:param configpath: path to a tenbilac config file
		:param name: to make it simple, don't give one. Just change the filename of your config file, this will be used as name.
		
		"""
		self.configpath = configpath
		
		if name is None: # We need such a "name" just for consistency, to make directories.
			self.name = os.path.splitext(os.path.split(self.configpath)[1])[0] # The filename itself
		else:
			self.name = name
		
	def __str__(self):
		return self.configpath
		

class TenbilacWrapper:
	"""
	Again, nothing to do, we keep this for consistency with other ML-packages.
	"""

	def __init__(self, params, workdir=None):
		
		self.params = params
		if workdir == None:
			self.workdir = "Tenbilac_workdir"
		else:
			self.workdir = workdir
		
		self.configlist=[("setup", "workdir", workdir)]
		
	def __str__(self):
		return "Tenbilac '%s' in %s" % (self.params.name, os.path.basename(self.workdir))

	
	def train(self, inputs, targets, auxinputs=None, inputnames=None, targetnames=None):
		"""
		Note that we might take over a previous training.
		
		:param inputs: a 3D numpy array, possibly masked, with indices (rea, feature, case)
		:param targets: a 2D array, with indices (feature, case)
		:param auxinputs: a 3D numpy array, optional		
		"""
		
		ten = tenbilac.com.Tenbilac(self.params.configpath, self.configlist)
		ten.train(inputs, targets, inputnames, targetnames)
		
	
	def predict(self, inputs):
		"""
		This works with 3D arrays.
		"""
		ten = tenbilac.com.Tenbilac(self.params.configpath, self.configlist)
		preds = ten.predict(inputs)
		return preds
	
		

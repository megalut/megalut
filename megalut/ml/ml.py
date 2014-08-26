"""
A module to connect the "Galaxies" and Machine Learning (ML) wrappers


"""

import skynetwrapper
#import ffnetwrapper
#import pybrainwrapper
import fannwrapper
#import minilut
	
import numpy as np
#import mlparams
from datetime import datetime
import os


class MLParams:
	"""
	A container for the general parameters describing the machine learning.
	
	The standart example with sextractor was :
	features = ["mes_g1", "mes_g2", "mes_size", "mes_flux", "mes_rad30", "mes_rad50", "mes_rad70", "mes_rad90"],
	labels = ["tru_g1", "tru_g2"]
	predlabels = ["pre_g1", "pre_g2"]
	
	
	Something that worked well with galsim was :
	features = ["mes_gs_g1", "mes_gs_g2", "mes_gs_sigma", "mes_gs_flux", "mes_gs_rho4"]

	
	"""
	
	def __init__(self, name, features, labels, predlabels, nb_committee=1):
		"""
		name is a string describing this ML run. Make sure it is unique for these parameters. Could contain a counter, of course.
		
		features and labels are lists of strings, with the names of the attributes of Galaxy objects to use
		- features is the list of attributes to be used as input
		- labels is the list of attributes you want me to predict.
		- predlabels is the corresponding list of attributes where I should write my predictions.
		
		"""
		
		self.name = name
		self.features = features
		self.labels = labels
		self.predlabels = predlabels
		self.nb_committee = nb_committee
		assert self.nb_committee >= 1
		assert len(self.labels) == len(self.predlabels)

		
		#self.method = method
		#assert self.method in ["skynet", "pybrain"]
		#self.methodpars = methodpars
		

	def __str__(self):
		txt = "ML parameters for %s:\n" % (self.name) + \
			"Features:    %s\n" % (", ".join(self.features)) + \
			"Labels:      %s\n" % (", ".join(self.labels)) + \
			"Predictions: %s\n" % (", ".join(self.predlabels)) + \
			"Nb Neural Network: %i" % (self.nb_committee)
		return txt




class ML:
	
	"""
	This is a class that will hopefully nicely wrap NN or other Machine Learning (ML) regression codes.
	So far it only uses skynet.py, but the idea is that it could do more later and stay very general.
	"""

	def __init__(self, mlparams, toolparams, workdir):
		"""
		features and labels are lists of strings, with the names of the attributes of Galaxy objects to use
		- features is the list of attributes to be used as input
		- labels is the list of attributes you want me to predict.
		- predlabels is the corresponding list of attributes where I should write my predictions.
		
		nndir is a directory in which the ML will work and store what it learned.
		"""
		
		self.mlparams = mlparams
		self.tool = toolparams.tool
		self.toolparams = toolparams
		self.workdir = workdir
		
		assert self.tool in ["skynet", "ffnet", "pybrain", "fann", "minilut"]
			
		self.objs=[]

		for nn_i in range(self.mlparams.nb_committee):

			nn_i_workdir=os.path.join(self.workdir,"%i" % nn_i)
			if self.tool == "skynet":
				self.objs.append(skynet.SkyNet(self.toolparams, workdir=nn_i_workdir)) # The instance of the ML code.
			elif self.tool == "ffnet":
				self.objs.append(ffnetwrapper.FfnetWrapper(self.toolparams, workdir=nn_i_workdir))
			elif self.tool == "pybrain":
				self.objs.append(pybrainwrapper.PyBrainWrapper(self.toolparams, workdir=nn_i_workdir))
			elif self.tool == "fann":
				self.objs.append(fannwrapper.FANNWrapper(self.toolparams, workdir=nn_i_workdir))
			elif self.tool == "minilut":
				self.objs.append(minilut.MiniLUT(self.toolparams, workdir=nn_i_workdir))
			else:
				raise RuntimeError("Not implemented !")
		
	
	def train(self, galaxies):
		"""
		galaxies is a list of Galaxy objects
		
		"""	
		starttime = datetime.now()
		
		for g in galaxies:
			g.calcmes() # Not sure if this is required, but doesn't harm...
#			if not g.isgood():
#				g.info()
#				exit()
	
		print "Training a ML in %s" % (self.workdir)
		print self.mlparams
		
		featuresdata = np.array([g.getattrs(self.mlparams.features) for g in galaxies])
		labelsdata = np.array([g.getattrs(self.mlparams.labels) for g in galaxies])
		
		for nn_i in range(self.mlparams.nb_committee):
			message = 'Training NN %s %i/%i' % (self.mlparams.name,nn_i+1,self.mlparams.nb_committee)
			print (len(message)+4)*'*'
			print '*', message, '*'
			print (len(message)+4)*'*'

			#self.objs[nn_i].train(features=featuresdata, labels=labelsdata) << That's all we do here
			if self.tool == "skynet":
				self.objs[nn_i].prep(features=featuresdata, labels=labelsdata)
				self.objs[nn_i].train(verbose=False)
			elif self.tool == "ffnet":
				self.objs[nn_i].train(features=featuresdata, labels=labelsdata)
			elif self.tool =="pybrain":
				self.objs[nn_i].train(features=featuresdata, labels=labelsdata)	
			elif self.tool =="fann":
				self.objs[nn_i].train(features=featuresdata, labels=labelsdata)
			elif self.tool =="minilut":
				self.objs[nn_i].train(features=featuresdata, labels=labelsdata)
			else:
				raise RuntimeError("Not implemented !")
	
		endtime = datetime.now()
		print "This ML training took %s" % (str(endtime - starttime))
	

	def predict(self, galaxies):
		"""
		Same idea as for train, but to compute predicted labels for your features.
		I will *update* the galaxies in place
		"""
		
		for g in galaxies:
			g.calcmes() # Not sure if this is required, but doesn't harm...

		preddata_list=[]
		for nn_i in range(self.mlparams.nb_committee):
			print "Predicting with ML in %s for NN %s %i/%i" % (self.mlparams.name,self.objs[nn_i].workdir,nn_i+1,self.mlparams.nb_committee)
			print self.mlparams
			print "Predicting %i galaxies" % (len(galaxies))
			 

			featuresdata = np.array([g.getattrs(self.mlparams.features) for g in galaxies])
			preddata_list.append(self.objs[nn_i].pred(featuresdata))

		
		for k, g in enumerate(galaxies):
			for i, predlabel in enumerate(self.mlparams.predlabels):
				listname = "%s_committee_%s_%s" % (predlabel, self.mlparams.name, self.toolparams.name)
				data=[]
				for nn_i in range(len(preddata_list)):
					#print nn_i, k, i
					data.append(preddata_list[nn_i][k,i])
				setattr(g, listname, data) # Save everything
				setattr(g, predlabel, np.mean(np.asarray(data))) # Take mean



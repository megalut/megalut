"""

Wrapper around pybrain

This is meant ot be generic, no "galaxies" here !

"""
import os
import numpy as np
from datetime import datetime
import utils


try:
	import pybrain
	import pybrain.tools.shortcuts
	import pybrain.datasets
	import pybrain.supervised.trainers
except:
	print "I can't import pybrain: not a problem if you don't use it."



class PyBrainParams:
	
	def __init__(self, nhid, name="pybrain"):
		
		self.nhid = nhid
		
		self.name = name
		self.tool = "pybrain"
		
		

class PyBrainWrapper:

	def __init__(self, params, workdir=None):
	
		if workdir == None:
			self.workdir = "pybraindir"
		else:
			self.workdir = workdir
			
		self.params = params
		
		
	def __str__(self):
		return "pybrain in %s" % (os.path.basename(self.workdir))



	
	def train(self, features, labels):
		
		if not os.path.isdir(self.workdir):
			os.mkdir(self.workdir)

		starttime = datetime.now()
		
		arch = [features.shape[1]]
		arch.extend(self.params.nhid)
		arch.append(labels.shape[1])
		
		self.arch = arch
		print "Network architecture : %s" % (str(self.arch))


		net = pybrain.tools.shortcuts.buildNetwork(*self.arch, bias=True)

		#print net
		
		ds = pybrain.datasets.SupervisedDataSet(features.shape[1], labels.shape[1])
		assert(features.shape[0] == labels.shape[0])
		ds.setField('input', features)
		ds.setField('target', labels)
		ds.linkFields(('input','target'))

		#print ds

		trainer = pybrain.supervised.trainers.BackpropTrainer(net, ds,
			learningrate=0.8, lrdecay=0.995, momentum=0.00, verbose=True)

		trainer.trainUntilConvergence(
			maxEpochs=50, verbose=True,
			continueEpochs=10, validationProportion=0.25,
			convergence_threshold=10
		)
		
		print net.params
		
		utils.writepickle(net, filepath = os.path.join(self.workdir, "pybrain_net.pkl"), verbose=True, protocol = -1)
		
		

	
	def pred(self, features):
		
		net = utils.readpickle(filepath = os.path.join(self.workdir, "pybrain_net.pkl"))
		
		output = np.array(map(net.activate, features))
		
		#output = np.array([net.activate(x) for x, _ in train])
		
		#print output
		
		return output
		
		
		

if __name__ == "__main__":
	"""
	A little demo and test !
	"""
	import matplotlib.pyplot as plt

	# Simple 1D case : we predict y(x) from noisy data points.
	
	x = np.random.uniform(-1.0, 1.0, 100)
	y = np.sin(5.0*x)*np.fabs(x) + 0.1*np.random.randn(len(x))
	
	# x and y are 1D arrays. But our SkyNet wrapper works only with 2D arrays.
	# First index = datapoint, sedond index : the different features.
	
	features = x.reshape(100, 1)
	labels = y.reshape(100, 1)
	
	snparams = PyBrainParams(nhid = [8])
	
	obj = PyBrainWrapper(snparams)
	
	obj.train(features, labels)
	
	# Let's make some predictions on a fine grid of points :
	pred_features = np.linspace(-2, 2, 1000).reshape(1000, 1)
	pred_labels = obj.pred(pred_features)
	
	plt.plot(x, y, "r.")
	plt.plot(pred_features, pred_labels, "g-")
	plt.xlabel("x")
	plt.ylabel("y")
	plt.show()
	

		
		
		
		

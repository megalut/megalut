"""
Wrapper around ffnet

This is meant ot be generic, no "galaxies" here !

"""
import os
import numpy as np
from datetime import datetime

try:
	import ffnet
except:
	print "I can't import ffnet: not a problem if you don't use it."




class FfnetParams:
	"""
	A container for the internal parameters for ffnet
	"""
	
	def __init__(self, nhid, name="ffnet"):
		"""
		nhid is a list of number of nodes in the hidden layers. example: [5] means one hidden layer with 5 nodes...
		"""
		self.nhid = nhid
		self.name = name # Just a string to identify this run...
		self.tool ="ffnet"



class FfnetWrapper:


	def __init__(self, params, workdir=None):
	
	
		if workdir == None:
			self.workdir = "ffnetdir"
		else:
			self.workdir = workdir
			
		self.params = params
		
	
	def __str__(self):
		return "ffnet in %s" % (os.path.basename(self.workdir))
		
	
	def train(self, features, labels):
		"""
		
		"""
		print "Starting the training of"
		print str(self)
		
		if not os.path.isdir(self.workdir):
			os.mkdir(self.workdir)

		starttime = datetime.now()
		
		arch = [features.shape[1]]
		arch.extend(self.params.nhid)
		arch.append(labels.shape[1])
		
		self.arch = arch
		print "Network architecture : %s" % (str(self.arch))
		
		conec = ffnet.mlgraph(arch, biases=True)
		
		net = ffnet.ffnet(conec)
		#import networkx as nx
		#nx.draw_graphviz(net.graph, prog='dot')
		#pylab.show()
		
		#net.train_genetic(features, labels, individuals=20, generations=20, verbosity=1)
		#net.test(features, labels, iprint=1)
		
		#net.train_tnc(input, target, maxfun = 5000, messages=1)
		net.train_tnc(features, labels, nproc=1, maxfun=100, messages=1)
		net.test(features, labels, iprint=1)
		
		
		ffnet.savenet(net, os.path.join(self.workdir, "ffnet.pkl"))
		
		endtime = datetime.now()
		print "This training took %s" % (str(endtime - starttime))
	
	
	def pred(self, features):
		"""
		
		"""
		print "Predicting with"
		print str(self)
		print "Network architecture : %s" % (str(self.arch))
		
		net = ffnet.loadnet(os.path.join(self.workdir, "ffnet.pkl"))
			
		pred = net(features)

		assert pred.shape[0] == np.shape(features)[0]

		return pred
	
	
		
		
		
		
		
		
		
		
		
		
		
		
	

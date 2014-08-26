"""

Wrapper around FANN, using pyfann that ships with FANN 2.1 beta

This is meant ot be generic, no "galaxies" here !

"""
import os
import numpy as np
from datetime import datetime
import utils


try:
	from pyfann import libfann
except:
	print "I can't import pyfann: not a problem if you don't use it."


def writedata(filename, inputs, outputs):#=None, noutput=1):
	"""
	Writes data files to be read by FANN, low level function
	
	#If you do not specify outputs (e.g., for predictions), I will write nouput zeroes.
	#Having the correct number of output labels seems mandatory for SkyNet.
	
	"""
	#if outputs == None:
	#	outputs = np.zeros(shape=(np.shape(inputs)[0], noutput))
	assert np.shape(inputs)[0] == np.shape(outputs)[0]
	ndp = np.shape(inputs)[0]
	nin = np.shape(inputs)[1]
	nout = np.shape(outputs)[1]
	f = open(filename, "w")
	f.write("%i %i %i\n" % (ndp, nin, nout))
	for inputline, outputline in zip(inputs, outputs):
		f.write(" ".join(["%.6f" % item for item in inputline]) + "\n")
		f.write(" ".join(["%.6f" % item for item in outputline]) + "\n")
	f.close()
	print "Wrote %s\n(datapoints : %i, inputs : %i, outputs : %i)" % (filename, ndp, nin, nout)



# The unsymmetric way :
"""
def standardize(data, params=None):

	if params == None:
		(mins, maxs) = (np.min(data, axis=0), np.max(data, axis=0))
	else:
		(mins, maxs) = params
		
		
	std_data = (data - mins)/(maxs - mins)
	std_data = 0.1 + 0.8 * std_data
	
	if params == None:
		return (std_data, (mins, maxs))
	else:
		return std_data
	

def unstandardize(data, params):
	
	(mins, maxs) = params
	unstd_data = (data - 0.1)/0.8
	unstd_data = mins + unstd_data * (maxs - mins)
	return unstd_data
"""


# Note that FANN does provide some scale unscale functions. Didn't see this.
def standardize(data, params=None, rangeval=1.0):
	"""
	output will be between -rangeval and +rangeval ...
	"""
	
	if params == None:
		(mins, maxs) = (np.min(data, axis=0), np.max(data, axis=0))
	else:
		(mins, maxs) = params
		
	std_data = (data - mins)/(maxs - mins)
	std_data = -rangeval + 2.0*rangeval * std_data
	
	if params == None:
		return (std_data, (mins, maxs))
	else:
		return std_data
	

def unstandardize(data, params, rangeval=1.0):
	
	(mins, maxs) = params
	unstd_data = (data + rangeval)/(2.0*rangeval)
	
	unstd_data = mins + unstd_data * (maxs - mins)
	return unstd_data






class FANNParams:
	
	def __init__(self, nhid, connection_rate=1.0,
			learning_rate=0.7, activation_steepness_hidden=0.5,
			desired_error=1.0e-7, max_iterations=10000, iterations_between_reports=None,
			rangeval = 1.0, activation_function_hidden = "SIGMOID_SYMMETRIC",
			name="fann", verbose=False):
		"""
		Choices for activation_function_hidden:
			SIGMOID_SYMMETRIC
			SIGMOID_SYMMETRIC_STEPWISE (same but faster)
			GAUSSIAN_SYMMETRIC
			ELLIOT_SYMMETRIC
			LINEAR_PIECE_SYMMETRIC
			
		
			
		"""
		
		self.nhid = nhid # a tuple of numbers of nodes per hidden layer
		self.connection_rate = connection_rate # controls how many connections there will be in the network. 
			# If the connection rate is set to 1, the network will be fully connected,
			# but if it is set to 0.5 only half of the connections will be set. 
			# A connection rate of 1 will yield the same result as fann_create_standard
		
		self.learning_rate = learning_rate
		self.activation_steepness_hidden = activation_steepness_hidden # Steepness of sigmoid for hidden nodes
		
		self.desired_error = desired_error
		self.max_iterations = max_iterations
		
		if iterations_between_reports == None:
			self.iterations_between_reports = self.max_iterations / 20
		else:
			self.iterations_between_reports = iterations_between_reports
		
		self.rangeval = rangeval
		self.activation_function_hidden = activation_function_hidden	
		
		self.name = name
		self.tool = "fann"
		self.verbose = verbose
		
		

class FANNWrapper:

	def __init__(self, params, workdir=None):
	
		if workdir == None:
			self.workdir = "FANNdir"
		else:
			self.workdir = workdir
			
		self.params = params
		
		
	def __str__(self):
		return "FANN in %s" % (os.path.basename(self.workdir))



	
	def train(self, features, labels):
		
		if not os.path.isdir(self.workdir):
			os.makedirs(self.workdir)

		starttime = datetime.now()
		
		arch = [features.shape[1]]
		arch.extend(self.params.nhid)
		arch.append(labels.shape[1])
		
		self.arch = arch
		print "Network architecture : %s" % (str(self.arch))
		
		ann = libfann.neural_net()
		#ann.create_standard_array(self.arch)
		ann.create_sparse_array(self.params.connection_rate, self.arch)
		
		ann.set_training_algorithm(libfann.TRAIN_RPROP)
		# TRAIN_INCREMENTAL
		# TRAIN_BATCH
		# TRAIN_RPROP == the default !
		# TRAIN_QUICKPROP
		# http://leenissen.dk/fann/html/files/fann_data-h.html#fann_train_enum
		
		
		ann.set_learning_rate(self.params.learning_rate)
		
		ann.set_activation_function_output(libfann.LINEAR) # IMPORTANT FOR REGRESSIONS !!!
		ann.set_activation_steepness_output(0.5) # No real influence, given the linear output layer.
		
		eval("ann.set_activation_function_hidden(libfann." + self.params.activation_function_hidden + ")")
		ann.set_activation_steepness_hidden(self.params.activation_steepness_hidden)

		(std_features, self.features_norm_params) = standardize(features, rangeval=self.params.rangeval)
		(std_labels, self.labels_norm_params) = standardize(labels, rangeval=self.params.rangeval)
		writedata(os.path.join(self.workdir, "input.data"), std_features, std_labels)
		
		if self.params.verbose:
			ann.print_parameters()
		
		#ann.randomize_weights(-0.2, 0.2) # They are already random, this does not seem to work anyway.
		
		ann.train_on_file(os.path.join(self.workdir, "input.data"), self.params.max_iterations, self.params.iterations_between_reports, self.params.desired_error)
		#ann.train_on_file(os.path.join(self.workdir, "input.data"), self.params.max_iterations, self.params.iterations_between_reports, self.params.desired_error)

		ann.save(os.path.join(self.workdir, "FANN.net"))
	
		
	
	
	def pred(self, features):
		
		ann = libfann.neural_net()
		ann.create_from_file(os.path.join(self.workdir, "FANN.net"))

		std_features = standardize(features, self.features_norm_params, rangeval=self.params.rangeval)
		std_output = np.array(map(ann.run, std_features))
		output = unstandardize(std_output, self.labels_norm_params, rangeval=self.params.rangeval)
		#output = std_output
		#print output
		
		return output
		
		

if __name__ == "__main__":
	"""
	A little demo and test !
	"""
	import matplotlib.pyplot as plt

	# Simple 1D case : we predict y(x) from noisy data points.
	
	
	n = 100
	x = np.random.uniform(0, 10, n)
	y = np.sin(x)*x + 0.3*np.random.randn(len(x))
	
	#x = np.random.uniform(-5, 10, n)
	#y = np.sin(x)*x + 0.3*np.random.randn(len(x))
	#y[x<=0] += 5
	
	
	
	# x and y are 1D arrays. But our SkyNet wrapper works only with 2D arrays.
	# First index = datapoint, sedond index : the different features.
	
	features = x.reshape(n, 1)
	labels = y.reshape(n, 1)
	
	
	for nhid in [10]:
	
		plt.clf()
		params = FANNParams(nhid = [nhid], learning_rate=0.5, max_iterations=1000, activation_steepness_hidden=0.5)
	
		obj = FANNWrapper(params)
		obj.train(features, labels)
	
		# Let's make some predictions on a fine grid of points :
		pred_features = np.linspace(-2, 12, 1000).reshape(1000, 1)
		pred_labels = obj.pred(pred_features)
	
		#print pred_labels.shape
		#print pred_features.shape
	
		plt.plot(x, y, "r.")
		plt.plot(pred_features, pred_labels, "b-")
		plt.xlabel("x")
		plt.ylabel("y")
		#plt.xlim(-7, 12)
		plt.xlim(-2, 12)
		
		plt.ylim(-10, 10)
		#plt.show()
		#plt.title("%i hidden nodes" % (nhid))
		#plt.savefig("%i.pdf" % (nhid))
		plt.show()

		
		
		
		

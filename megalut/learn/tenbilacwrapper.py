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
	
	"""
	
	
	def __init__(self, hidden_nodes, errfctname="msrb", n=1, max_iterations=100, gtol=1e-8,
		valfrac=0.5, shuffle=True, mbsize=None, mbfrac=0.1, mbloops=1,
		startidentity=True, ininoisewscale=0.1, ininoisebscale=0.1,
		normtargets=True, normtype="-11", actfctname="tanh", oactfctname="iden",
		verbose=False, name="default", reuse=True, autoplot=True, keepdata=False):
		"""
		
		:param hidden_nodes: list giving the number of nodes per hidden layer
		:param max_itrations: 
		:param errfct: either "msb" or "msrb"
		:param n: number of tenbilac instances to train
		:param normtargets: if True, targets will be normed, and the predictions will be denormed using the same normer.
			This is what you want for conventional networks that predict "labels".
			But when predicting weights, set this to False to not have the targets normalized.
		:param normtype:
		:param actfct: either "sig" or "tanh"
		:param name:
		
		:param reuse: if True, will start the training from the existing state (if available)
		
		:param keepdata: if True, the data is kept in the final pickle saved once the training is done.
			Can be useful for plots and debugging, but is huge.
		
		
		
		"""
		self.hidden_nodes = hidden_nodes 
		self.max_iterations = max_iterations
		self.gtol = gtol
		self.errfctname = errfctname
		self.nmembers = n
		self.valfrac = valfrac
		self.shuffle = shuffle
		self.mbsize = mbsize
		self.mbfrac = mbfrac
		self.mbloops = mbloops
		self.startidentity = startidentity
		self.ininoisewscale = ininoisewscale
		self.ininoisebscale = ininoisebscale
		self.normtargets = normtargets
		self.normtype = normtype
		self.actfctname = actfctname
		self.oactfctname = oactfctname
		self.verbose = verbose
		self.name = name
		self.reuse = reuse
		self.autoplot = autoplot
		self.keepdata = keepdata
		self.ncpu = 1 # This is the default value, which will get overwritten by run (learn)
		
	def __str__(self):
		return "Tenbilac parameters \"{self.name}\" ({self.hidden_nodes}, {self.max_iterations}, {self.normtype}, {self.actfctname}, {self.errfctname})".format(self=self)
		

class TenbilacWrapper:

	def __init__(self, params, workdir=None):

		if workdir == None:
			self.workdir = "Tenbilac_workdir"
		else:
			self.workdir = workdir
			
		# Setting up the workdir:
		if not os.path.isdir(self.workdir):
			os.makedirs(self.workdir)
		else:
			logger.info("Tenbilac workdir %s already exists" % self.workdir)
			
		# Define the directories in which the files are saved for each committee member:
		
		# We open a file object:
		
		self.memberdirpaths = []
		self.memberfiles = []
		for ii in range(params.nmembers):
			# Now we can get the unique filename
			cfname = "member_{:03d}".format(ii)
			
			cdir = os.path.join(workdir, cfname)
			
			self.memberdirpaths.append(cdir) 
			
			# Setting up the workdir:
			if not os.path.isdir(cdir):
				os.makedirs(cdir)
			else:
				logger.info("Tenbilac instance workdir %s already exists" % cdir)
			
			self.memberfiles.append(os.path.join(cdir, "Tenbilac.pkl"))
					
		#self.netpath = os.path.join(self.workdir, "Tenbilac.pkl")
		self.netpath = os.path.join(self.workdir, "CommitteeTenbilac.pkl")
		self.params = params
		
		
	def __str__(self):
		return "Tenbilac '%s' in %s" % (self.params.name, os.path.basename(self.workdir))

	
	def train(self, inputs, targets, auxinputs=None, inputnames=None, targetnames=None):
		"""
		Note that we might take over a previous training.
		
		:param inputs: a 3D numpy array, possibly masked, with indices (rea, feature, case)
		:param targets: a 2D array, with indices (feature, case)
		
		:param auxinputs: a 3D numpy array, optional		
		"""
			
		# Some tests to start with
		assert inputs.ndim == 3
		assert targets.ndim == 2
		
		# We normalize the inputs and labels, and save the Normers for later denormalizing.
		logger.info("{0}: normalizing training inputs...".format((str(self))))
		self.input_normer = tenbilac.data.Normer(inputs, type=self.params.normtype)
		norminputs = self.input_normer(inputs)
		
		if self.params.normtargets:
			logger.info("{0}: normalizing training targets...".format((str(self))))
			self.target_normer = tenbilac.data.Normer(targets, type=self.params.normtype)
			normtargets = self.target_normer(targets)
		else:
			logger.info("{0}: I do NOT normalize targets...".format((str(self))))
			self.target_normer = None
			normtargets = targets

		# Hmm, we do not normalize the auxinputs, this would seem weird.
		# But maybe we should think about normalizing the network outputs, instead of the targets.
		
		# Now we take care of setting up the network (even if we might reuse an existing one)
		ni = inputs.shape[1]
		nhs = self.params.hidden_nodes
		no = targets.shape[0]
		
		# Short-hand:
		ncm = self.params.nmembers
		
		#TODO: implement the choice of many different configs/trainings
		logger.info("{:s}: is a committee of {:d} member(s)".format(str(self), self.params.nmembers))
		comm_members = [tenbilac.net.Net(ni, nhs, no, actfctname=self.params.actfctname, oactfctname=self.params.oactfctname,
			inames=inputnames, onames=targetnames, name='commid={cid}'.format(cid=ii)) for ii in range(self.params.nmembers)]
		comm = tenbilac.committee.Committee(comm_members)
				
		# We can prep the traindata object:
		dat = tenbilac.data.Traindata(inputs=norminputs, targets=normtargets, auxinputs=auxinputs, 
									valfrac=self.params.valfrac, shuffle=self.params.shuffle)

		# Let's see if an existing training is available (before the init of the new training writes its file...)
		oldtrain = None
		if os.path.exists(self.netpath) and self.params.reuse:
			# Then we try to read the existing training and start the training from it's parameters.
			logger.info("Reading in existing training... ")
			oldtrain = tenbilac.utils.readpickle(self.netpath)			
			
		# And set up the training object:
		ctraining = tenbilac.committee.CommTraining(comm, dat=[dat]*ncm, 
				errfctname=[self.params.errfctname]*ncm,
				itersavepath=self.memberfiles,
				autoplotdirpath=self.memberdirpaths,
				verbose=[self.params.verbose]*ncm,
				autoplot=[self.params.autoplot]*ncm,
				name=[self.params.name]*ncm,
				multiple_trainings=True)
	
		# And now see if we take over the previous training or not:
		if oldtrain is None:
			if self.params.startidentity:
				ctraining.call('setidentity', attr='net')
			ctraining.call(attr='net', method='addnoise', wscale=self.params.ininoisewscale, bscale=self.params.ininoisebscale)
						
		else:
			logger.info("Reusing previous network!")
			for ii in range(len(oldtrain.trainings)):
				ctraining.trainings[ii].takeover(oldtrain.trainings[ii])

		# Ready!

		logger.info("{0}: starting the training".format((str(self))))
		
		ctraining.call(method='minibatch_bfgs', call_ncpu=self.params.ncpu, mbsize=self.params.mbsize, 
			mbfrac=self.params.mbfrac, mbloops=self.params.mbloops,
			maxiter=self.params.max_iterations, gtol=self.params.gtol)
		
		ctraining.save(self.netpath, self.params.keepdata)
	
		logger.info("{0}: done with the training".format((str(self))))
		
	
	
	def predict(self, inputs):
		"""
		This works with 3D arrays.
		"""
			
		# We read the Tenbilac:
		ctraining = tenbilac.utils.readpickle(self.netpath)
		comm = ctraining.committee
		
		logger.info("{0}: normalizing inputs for prediction...".format((str(self))))
		norminputs = self.input_normer(inputs)
		
		# As simple as this:	
		normpreds = comm.call("predict", inputs=norminputs)
		
		# Those normpreds are appropriately masked.
		# We de-normalise these predictions
		if self.params.normtargets:
			preds = self.target_normer.denorm(normpreds)
		else:
			preds = normpreds

		return preds
	
		

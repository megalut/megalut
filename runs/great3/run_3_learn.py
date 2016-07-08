import megalut.tools as tools
import megalut.learn as learn

import config
import mymlparams

import megalutgreat3 as mg3

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)

#TODO: What about the validation set?
#TODO: need to implement committees

# Loading the correct configuration!
great3 = mg3.great3.load_config(outdir='cgc')

# Choose a training configuration
trainparamslist = mymlparams.trainparams['list'] 
trainname = mymlparams.trainparams['name'] 

# The simulation used by default in training is the one defined in:
# great3.simparams_name
simparams_name = great3.simparams_name

for subfield in config.subfields:
	
	# Getting the path to the correct directories
	simdir = great3.get_path("sim","%03i" % subfield)
	traindir = great3.get_path("ml", "%03i" % subfield, trainname, simparams_name)
	
	# We load the right catalog (location depends on simname):
	cat = tools.io.readpickle(great3.get_path("simmeas", "%03i" % subfield, simparams_name, "groupmeascat.pkl"))
	
	# Let's go for training
	learn.run.train(cat, traindir, trainparamslist, ncpu=1)#config.ncpu)

# Remembering the name of the trainparams:
great3.trainparams_name = trainname
great3.trainparamslist = mymlparams.trainparams['list'] 
great3.save_config()

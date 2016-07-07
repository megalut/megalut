import os
import numpy as np

import megalut.tools as tools
import megalut.learn as learn

import config

import megalutgreat3 as mg3
import metrics

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Loading the correct configuration!
great3 = mg3.great3.load_config(outdir='cgc')

# The training used by default in training is the one defined in:
# great3.trainparams_name
trainname = great3.trainparams_name
trainparamslist = great3.trainparamslist

# The simulation used by default in training is the one defined in:
# great3.simparams_name
simparams_name = great3.simparams_name

for subfield in great3.subfields:
	
	# Getting the path to the correct directories
	simdir = great3.get_path("sim","%03i" % subfield)
	measdir = great3.get_path("simmeas", "%03i" % subfield)
	traindir = great3.get_path("ml", "%03i" % subfield, trainname, simparams_name)
	
	# We read the obs measurements
	cat = tools.io.readpickle(great3.get_path("obs", "img_%i_meascat.pkl" % subfield))
	
	# Predicting the training data
	cat = learn.run.predict(cat, traindir, trainparamslist)
	tools.io.writepickle(cat, os.path.join(traindir, "predtraincat.pkl"))
	
	# And we save the predictions
	predir = great3.get_path("pred", "%03i" % subfield, trainname, simparams_name)
	
	if not os.path.exists(predir):
		os.makedirs(predir)
	
	tools.io.writepickle(cat, os.path.join(predir, "preobscat.pkl"))
	
	# Formating for the out catalogues
	# We replace masked predictions with 20.0
	cat["pre_s1"][cat["pre_s1"].mask] = 20.0
	cat["pre_s2"][cat["pre_s2"].mask] = 20.0
	
	# We cut out the columns we need
	preobscat = cat["ID","pre_s1","pre_s2"]
	
	# We write the ascii file
	preobscat.write(great3.get_path("out", "%03i.cat" % subfield), format="ascii.commented_header")
	
	logger.info("Wrote shear cat for subfield %03i" % subfield)

logger.info("Pre-submitting the catalogs")

great3.presubmit(corr2path=config.corr2path, presubdir=config.presubdir)

logger.info("Evaluating with the Great3 code")

submission_file = great3.get_path("out", "%s.cat" % great3.branchcode())

results = metrics.evaluate.q_constant(submission_file, great3.experiment, great3.obstype, logger=logger)
Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx = results

np.savetxt(great3.get_path('out', 'results_%s.cat' % great3.branchcode()), results,\
		 header='Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx')
logging.info('Q value: %1.2f' % Q_c) 

import os
import numpy as np

import megalut.tools as tools

import config

import megalutgreat3 as mg3
import metrics.evaluate as evaluate

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

fields_id, fields_true_e1, fields_true_e2 = evaluate.get_generate_const_truth(great3.experiment, great3.obstype, logger=logger)

mean_g1 = []
mean_g2 = []
for subfield in config.subfields:

	# We load the predictions
	predir = great3.get_path("pred", "%03i" % subfield, trainname, simparams_name)
	
	cat = tools.io.readpickle(os.path.join(predir, "preobscat.pkl"))
	
	# Formating for the out catalogues
	# We replace masked predictions with 20.0
	
	mean_g1.append(np.mean(cat["pre_g1"]))
	mean_g2.append(np.mean(cat["pre_g2"]))

	cat["pre_g1"][cat["pre_g1"].mask] = 20.0
	cat["pre_g2"][cat["pre_g2"].mask] = 20.0
	
	# We cut out the columns we need
	preobscat = cat["ID","pre_g1","pre_g2"]
	
	# We write the ascii file
	preobscat.write(great3.get_path("out", "%03i.cat" % subfield), format="ascii.commented_header")
	
	logger.info("Wrote shear cat for subfield %03i" % subfield)
	
import pylab as plt
plt.scatter(config.subfields, mean_g1, marker="*", c='k', s=100, label="meas e1")
plt.scatter(config.subfields, mean_g2, marker="*", c='r', s=100, edgecolor='r', label="meas e2")

plt.scatter(config.subfields, fields_true_e1[config.subfields], marker="o", c='k', edgecolor='Grey', s=20, label="true e1")
plt.scatter(config.subfields, fields_true_e2[config.subfields], marker="o", c='r', edgecolor='Grey', s=20, label="true e2")

plt.xlabel("Sub-field ID")
plt.ylabel("Constant ellipticity value")

plt.legend(loc='best')
plt.grid()

plt.show()


logger.info("Pre-submitting the catalogs")

great3.presubmit(corr2path=config.corr2path, presubdir=config.presubdir)

logger.info("Evaluating with the Great3 code")

submission_file = great3.get_path("out", "%s.cat" % great3.branchcode())

results = evaluate.q_constant(submission_file, great3.experiment, great3.obstype, logger=logger, plot=True, pretty_print=True)
Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx = results

np.savetxt(great3.get_path('out', 'results_%s.cat' % great3.branchcode()), results,\
		 header='Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx')
logging.info('Q value: %1.2f' % Q_c) 

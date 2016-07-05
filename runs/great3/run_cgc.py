import megalutgreat3 as mg3

import g3measfct as measfct
import mysimparams
import mymlparams
import plots
import config
import os
import metrics
import numpy as np

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)

# Create an instance of the GREAT3 class
run = mg3.great3.Run("control", "ground", "constant",
	datadir = config.datadir,
	workdir = config.workdir,
	subfields = config.subfields)

# Measuring the PSFs (the handling of positions and files is done by the G3 wrapper)
#wp#run.meas_psf(measfct.psf)

# Getting the raw shape measurements using SExtractor and sewpy
#wp#run.meas_obs(measfct.galaxies, skipdone=config.skipdone, ncpu=config.ncpu) 

# Make simulations
simparams = mysimparams.Ground_v1('ground_v1')
#wp#run.make_sim(simparams, n=10, ncat=5, nrea=2, ncpu=config.ncpu)

# Measure them
#wp#run.meas_sim(simparams, measfct.galaxies,
#wp#	groupcols=measfct.groupcols, removecols=measfct.removecols, ncpu=config.ncpu)

# Start training
#TODO: What about the validation set?
#TODO: need to implement committees
#wp#run.train(trainparams=mymlparams.default_tripletwenty, trainname="default_tripletwenty", simname=simparams.name, ncpu=config.ncpu)

# Looking at the results
#wp#run.self_predict(trainparams=mymlparams.default_tripletwenty, trainname="default_tripletwenty", simname=simparams.name)
#wp#plots.presimcheck(run, trainname="default_tripletwenty", simname=simparams.name, outdir=os.path.join(run.workdir, 'pred'), show=False)

#wp#run.predict(trainparams=mymlparams.default_tripletwenty, trainname="default_tripletwenty", simname=simparams.name, suffix='_mean', suffixcols=measfct.groupcols)

#wp#run.writeout(trainname="default_tripletwenty", simname=simparams.name)

#wp#run.presubmit(corr2path=config.corr2path, presubdir=config.presubdir)

submission_file = run._get_path("out", "%s.cat" % run.branchcode())
results = metrics.evaluate.q_constant(submission_file, run.experiment, run.obstype, logger=logging.getLogger(__name__))
Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx = results

np.savetxt(os.path.join(run.workdir, 'out', 'results_%s.cat' % run.branchcode()), results,\
		 header='Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx')
logging.info('Q value: %1.2f' % Q_c) 


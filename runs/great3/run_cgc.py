import megalutgreat3 as mg3

import g3measfct as measfct
import mysimparams
import mymlparams
import plots
import config

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)

# Create an instance of the GREAT3 class
run = mg3.great3.Run("control", "ground", "constant",
	datadir = config.datadir,
	workdir = config.workdir,
	subfields = config.subfields)

# Measuring the PSFs (the handling of positions and files is done by the G3 wrapper)
run.meas_psf(measfct.psf)

# Getting the raw shape measurements using SExtractor and sewpy
run.meas_obs(measfct.galaxies, skipdone=config.skipdone, ncpu=config.ncpu) 

# Make simulations
simparams = mysimparams.Ground_v1('ground_v1')
run.make_sim(simparams, n=10, ncat=5, nrea=2, ncpu=config.ncpu)

# Measure them
run.meas_sim(simparams, measfct.galaxies,
	groupcols=measfct.groupcols, removecols=measfct.removecols, ncpu=config.ncpu)

# Start training
#TODO: What about the validation set?
run.train(trainparams=mymlparams.default_tripletwenty, trainname="default_tripletwenty", simname=simparams.name, ncpu=config.ncpu)

# Looking at the results
#run.self_predict(trainparams=mymlparams.default_tripletwenty, trainname="default_tripletwenty", simname=simparams.name)
#plots.presimcheck(run, trainname="default_tripletwenty", simname=simparams.name)

run.predict(trainparams=mymlparams.default_tripletwenty, trainname="default_tripletwenty", simname=simparams.name, suffix='_mean', suffixcols=measfct.groupcols)

run.writeout(trainname="default_tripletwenty", simname=simparams.name)

run.presubmit(corr2path=config.corr2path, presubdir=config.presubdir)

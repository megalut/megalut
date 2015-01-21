
import megalut.great3

import sewpymeasfct as measfct
import mysimparams
import mymlparams
import plots
import config

import logging
logging.basicConfig(format='%(asctime)s %(levelname)s: %(name)s(%(funcName)s): %(message)s', level=logging.DEBUG)

# Create an instance of the GREAT3 class
run = megalut.great3.great3.Run("control", "space", "constant",
	datadir = config.datadir,
	workdir = config.workdir,
	subfields = config.subfields)

#run.subfields = [0]
#simparams = mysimparams.space_v1

simparams = mysimparams.Space_v1("Space_v1_n25_nrea30")


# Measure the stars (PSFs)
run.meas_psf(measfct.psf, skipdone=config.skipdone)


# Run measurements on input images
run.meas_obs(measfct.galaxies, skipdone=config.skipdone, ncpu=config.ncpu)


# Make simulations
run.make_sim(simparams, n=10, ncat=2, nrea=3, ncpu=config.ncpu)

# Measure them
run.meas_sim(simparams, measfct.galaxies,
	groupcols=measfct.groupcols, removecols=measfct.removecols, ncpu=config.ncpu)

plots.simobscompa(run, simparams)

# default:

run.train(trainparams=mymlparams.default_simpleten, trainname="default_simpleten", simname=simparams.name, ncpu=config.ncpu)
run.self_predict(trainparams=mymlparams.default_simpleten, trainname="default_simpleten", simname=simparams.name)

plots.presimcheck(run, trainname="default_simpleten", simname=simparams.name)


"""
# rea0:
run.train(trainparams=mymlparams.rea0_doubletwenty, trainname="rea0_doubletwenty", simname=simparams.name, ncpu=4)
run.self_predict(trainparams=mymlparams.rea0_doubletwenty, trainname="rea0_doubletwenty", simname=simparams.name)
plots.presimcheck(run, trainname="rea0_doubletwenty", simname=simparams.name)
"""

run.predict(trainparams=mymlparams.default_simpleten, trainname="default_simpleten", simname=simparams.name)

run.writeout(trainname="default_simpleten", simname=simparams.name)

run.presubmit(corr2path=config.corr2path, presubdir=config.presubdir)


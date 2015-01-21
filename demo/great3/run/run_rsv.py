
import megalut.great3


import sewpymeasfct as measfct
import mysimparams
import mymlparams
import plots

import logging
logging.basicConfig(format='%(asctime)s \033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)


# Create an instance of the GREAT3 class
run = megalut.great3.great3.Run("real_galaxy", "space", "variable",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_v5_GREAT3_run77_RSV",
	subfields = range(0, 200, 20))


simparams = mysimparams.Space_v1("Space_v1_n30_nrea30")

"""
run.subfields = range(0, 200)
# Measure the stars (PSFs)
run.meas_psf(measfct.psf)

# Run measurements on input images
run.meas_obs(measfct.galaxies, skipdone=False, ncpu=4)
"""
"""
#run.subfields = range(0, 200, 20)
#run.subfields = [0]
run.subfields = range(20, 200, 20)


# Make simulations
run.make_sim(simparams, n=30, ncat=1, nrea=30, ncpu=4)


# Measure them
run.meas_sim(simparams, mymeasfct.sewpyadamom,
	groupcols=mymeasfct.sewpyadamom_groupcols, removecols=mymeasfct.sewpyadamom_removecols, ncpu=4)


#plots.simobscompa(run, simparams)


run.train(trainparams=mymlparams.default_doubleten, trainname="default_doubleten", simname=simparams.name, ncpu=4)
run.self_predict(trainparams=mymlparams.default_doubleten, trainname="default_doubleten", simname=simparams.name)

#plots.presimcheck(run, trainname="default_doubleten", simname=simparams.name)

"""

run.subfields = range(200)

run.predict(trainparams=mymlparams.default_simpleten, trainname="default_simpleten", simname=simparams.name)

run.writeout(trainname="default_simpleten", simname=simparams.name)

run.presubmit(corr2path = "/users/mtewes/GREAT3/mjarvis-read-only", presubdir="/users/mtewes/GREAT3/great3-public-svn/presubmission_script")



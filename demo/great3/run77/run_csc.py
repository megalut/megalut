
import megalut.great3


import mymeasfct
import mysimparams
import mymlparams
import plots

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)


# Create an instance of the GREAT3 class
run = megalut.great3.great3.Run("control", "space", "constant",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_v5_GREAT3_run77",
	subfields = range(10))


simparams = mysimparams.space_v1


"""
# Measure the stars (PSFs)
run.meas_psf(mymeasfct.psf_sewpyadamom)

# Run measurements on input images
run.meas_obs(mymeasfct.sewpyadamom, skipdone=False, ncpu=10)

# Make simulations
run.make_sim(simparams, n=100, ncat=1, nrea=30, ncpu=10)

# Measure them
run.meas_sim(simparams, mymeasfct.sewpyadamom,
	groupcols=mymeasfct.sewpyadamom_groupcols, removecols=mymeasfct.sewpyadamom_removecols, ncpu=10)

"""

run.subfields = [0]

#plots.simobscompa(run, simparams)

#run.train(trainparams=mymlparams.default_doubletwenty, trainname="default_doubletwenty", simname=simparams.name, ncpu=4)

#run.self_predict(trainparams=mymlparams.default_doubletwenty, trainname="default_doubletwenty", simname=simparams.name)

plots.presimcheck(run, trainname="default_doubletwenty", simname=simparams.name)




"""
# Predict the output
cgv.predict()

# Write the output catalog
cgv.writeout("ML_FANN_demo_default")

# Prepare the presubmission file
# (This will fail as we work only on a subset of the data)
cgv.presubmit()
"""

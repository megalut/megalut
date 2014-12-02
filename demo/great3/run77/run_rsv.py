
import megalut.great3


import mymeasfct
import mysimparams
import mymlparams
import plots

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)


# Create an instance of the GREAT3 class
run = megalut.great3.great3.Run("real_galaxy", "space", "variable",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_v5_GREAT3_run77_RSV",
	subfields = range(0, 200, 20))


simparams = mysimparams.space_v1


run.subfields = range(0, 200)
# Measure the stars (PSFs)
run.meas_psf(mymeasfct.psf_sewpyadamom)

# Run measurements on input images
run.meas_obs(mymeasfct.sewpyadamom, skipdone=False, ncpu=4)


run.subfields = range(0, 200, 20)
# Make simulations
run.make_sim(simparams, n=100, ncat=1, nrea=20, ncpu=4)

"""
# Measure them
run.meas_sim(simparams, mymeasfct.sewpyadamom,
	groupcols=mymeasfct.sewpyadamom_groupcols, removecols=mymeasfct.sewpyadamom_removecols, ncpu=10)

"""

#plots.simobscompa(run, simparams)


"""
# Train the ML
cgv.learn(learnparams=learnparams, mlparams=fannparams, simparam_name=simparam_name, 
          method_prefix="adamom_",suffix="_mean")

# Predict the output
cgv.predict()

# Write the output catalog
cgv.writeout("ML_FANN_demo_default")

# Prepare the presubmission file
# (This will fail as we work only on a subset of the data)
cgv.presubmit()
"""

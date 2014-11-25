
import megalut.great3
import megalut.meas
import megalut.sim
import megalut.learn

import demo_measfct
import demo_simparams
import demo_mlparams

import numpy as np

import logging
logging.basicConfig(level=logging.DEBUG)



# Create an instance of the GREAT3 class
run = megalut.great3.great3.Run("control", "ground", "variable",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_v5_GREAT3",
	subfields = range(5,10))

# Run measurements on input images
run.meas_obs(demo_measfct.sewpyadamom, skipdone=True, ncpu = 5)

exit()

# Make sim catalogs & images
cgv.sim(cgv_simparm,n=10,ncpu=0,nrea=8)

# Measure the observations with the same methods than the observation
cgv.meas("sim",measfct,measfctkwargs,ncpu=0,simparams=cgv_simparm)

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

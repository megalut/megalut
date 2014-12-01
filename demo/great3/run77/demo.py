
import megalut.great3


import mymeasfct
import mysimparams
import mymlparams


import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)


# Create an instance of the GREAT3 class
run = megalut.great3.great3.Run("control", "ground", "variable",
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_v5_GREAT3_run77",
	subfields = range(3))

# Run measurements on input images
run.meas_obs(mymeasfct.sewpyadamom, skipdone=False, ncpu=3)

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

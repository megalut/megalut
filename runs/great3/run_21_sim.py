"""
Simulates a dedicated training set for each subfield.
"""


import megalut
import megalut.meas
import config
import numpy as np
import os


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

import simparams
import measfcts

# Loading the run
great3 = config.load_run()


# Choose a model for the simulations

sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_train_nn"
sp.snc_type = 1
sp.shear = 0
sp.noise_level = 0.0
sp.distmode = "uni"
n = 400
nc = 20
nrea = 10 # Even without noise, there is still the position jitter and pixelization
ncat = 5
ncpu = config.ncpu

"""

sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_simobscompa"
sp.snc_type = 1
sp.shear = 0
sp.noise_level = 1
sp.distmode = "G3"
n = 1000
nc = 10
nrea = 1
ncat = 1
ncpu = 1


"""
"""
sp = simparams.G3CGCSersics()
sp.name = "G3CGCSersics_valid" # To check the training, with shear and SNC, 500 cases
sp.snc_type = 10000
sp.shear = 0.1
sp.noise_level = 1
sp.distmode = "uni"
n = 1
nc = 1
nrea = 1
ncat = 25
ncpu = 25
"""


for subfield in config.subfields:
	
	# We have to read in the obs catalog of this subfield to get the noise of the sky:
	if sp.noise_level != 0:
		obscat = megalut.tools.io.readpickle(great3.path("obs", "img_%i_meascat.pkl" % subfield))
		sp.noise_level = np.ma.mean(obscat["skymad"])
		logger.info("Noise level set to {}".format(sp.noise_level))
	
	# Getting the path to the correct directories
	simdir = great3.path("sim","%03i" % subfield)
	measdir = great3.path("simmeas","%03i" % subfield)
	
	# Loading the PSF for the subfield
	psfcat = megalut.tools.io.readpickle(great3.path("obs", "star_%i_meascat.pkl" % subfield))
	

	# Simulating images
	megalut.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":n, "nc":nc, "stampsize":great3.stampsize()},
		drawimgkwargs={}, 
		psfcat=psfcat, psfselect="random",
		ncat=ncat, nrea=nrea, ncpu=ncpu,
		savepsfimg=False, savetrugalimg=False
	)


	# Measuring the newly drawn images
	megalut.meas.run.onsims(
		simdir=simdir,
		simparams=sp,
		measdir=measdir,
		measfct=measfcts.gal,
		measfctkwargs={"branch":great3},
		ncpu=ncpu,
		skipdone=config.skipdone
	)


	cat = megalut.meas.avg.onsims(
		measdir=measdir, 
		simparams=sp,
		task="group",
		groupcols=measfcts.groupcols, 
		removecols=measfcts.removecols
	)

	megalut.tools.table.keepunique(cat)
	megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))



## Remembering the name of the simparams:
#great3.simparams_name = sp.name
#great3.save_config()

"""
Simulates a dedicated training set for each subfield.
"""


import megalut
import config
import simparams

import g3measfct as measfct

import megalutgreat3 as mg3

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)


# Loading the run
great3 = config.load_run()

# Choose a model for the simulations
sp = mysimparams.Sersics()



IS NOT YET DONE



for subfield in config.subfields:
	
	# We have to read in the obs catalog of this subfield to get the noise of the sky:
	#obscat = tools.io.readpickle(great3.path("obs", "img_%i_meascat.pkl" % subfield))
	#sig = np.ma.mean(obscat["skymad"])
	#sp.sig = sig
	
	# Getting the path to the correct directories
	simdir = great3.path("sim","%03i" % subfield)
	measdir = great3.path("simmeas","%03i" % subfield)
	
	# Loading the PSF for the subfield
	psfcat = tools.io.readpickle(great3.path("obs", "star_%i_meascat.pkl" % subfield))
	
	
	# Simulating images
	sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":1000, "nc":10, "stampsize":great3.stampsize()},
		drawimgkwargs={}, 
		psfcat=psfcat, psfselect="random",
		ncat=1, nrea=2, ncpu=config.ncpu,
		savepsfimg=False, savetrugalimg=False
	)

	# Measuring the newly drawn images
	meas.run.onsims(
		simdir=simdir,
		simparams=sp,
		measdir=measdir,
		measfct=measfct.galaxies,
		measfctkwargs={"branch":great3},
		ncpu=config.ncpu,
		skipdone=config.skipdone
	)


	cat = meas.avg.onsims(
		measdir=measdir, 
		simparams=sp,
		task="group",
		groupcols=measfct.groupcols, 
		removecols=measfct.removecols
	)

	tools.table.keepunique(cat)
	tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))

## Remembering the name of the simparams:
#great3.simparams_name = sp.name
#great3.save_config()

"""
Simulates a single training set for all subfields.
"""


import megalut
import megalutgreat3

import config
import simparams


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)



great3 = config.load_run()


simdir = great3.path("sim", "allstars")
sp = simparams.Sersics()

psfcat = megalut.tools.io.readpickle(great3.path("obs", "allstars_meascat.pkl"))
	

# To train for shear, we want 

megalut.sim.run.multi(
	simdir=simdir,
	simparams=sp,
	drawcatkwargs={"n":20, "nc":10, "stampsize":great3.stampsize()},
	drawimgkwargs={}, 
	psfcat=psfcat,
	psfselect="random",
	ncat=1, nrea=1, ncpu=config.ncpu,
	savepsfimg=False,
	savetrugalimg=False
	)



"""
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
"""

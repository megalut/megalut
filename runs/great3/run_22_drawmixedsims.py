"""
Simulates a single training set for all subfields.

It's safe to uncomment run / meas / avg one after the other.
"""


import megalut
import megalutgreat3

import config
import simparams
import measfcts


import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)



great3 = config.load_run()

psfcat = megalut.tools.io.readpickle(great3.path("obs", "allstars_meascat.pkl"))
#print psfcat
#exit()

simdir = great3.path("sim", "allstars")
measdir = great3.path("simmeas", "allstars")
sp = simparams.CGCSersics()
	



# Generate catalogs and draw the corresponding stamps, using galsim, 
megalut.sim.run.multi(
	simdir=simdir,
	simparams=sp,
	drawcatkwargs={"n":100, "nc":1, "stampsize":great3.stampsize()},
	drawimgkwargs={}, 
	psfcat=psfcat,
	psfselect="random",
	ncat=10, nrea=1, ncpu=config.ncpu,
	savepsfimg=False,
	savetrugalimg=False
	)




# Run the feature measuements on those stamps:
megalut.meas.run.onsims(
	simdir=simdir,
	simparams=sp,
	measdir=measdir,
	measfct=measfcts.gal,
	measfctkwargs={"branch":great3},
	ncpu=config.ncpu,
	skipdone=config.skipdone
)

# This leaves us with one meascat per FITS image





# Group those results into one single catalog
# There is not that much to do here, as we haven't used nrea

cat = megalut.meas.avg.onsims(
	measdir=measdir, 
	simparams=sp,
	task="group",
	groupcols=measfcts.groupcols, 
	removecols=measfcts.removecols
)

megalut.tools.table.keepunique(cat)
megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))






# Restructure this flat catalog to define "cases" and "realizations" for the machine learning (i.e., make it a 3D catalog).

cat = megalut.tools.io.readpickle(os.path.join(measdir, sp.name, "groupmeascat.pkl"))
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat_cases.pkl"))





# Remembering the names to make it easier to find those files:
great3.simparams = sp
great3.simdir = simdir
great3.measdir = measdir
great3.save_run()


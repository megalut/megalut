

import megalut
import config
import measfcts
import simparams
import glob
import os
import numpy as np
import astropy

import logging
logger = logging.getLogger(__name__)



psfcat = megalut.tools.io.readpickle(config.psfcatpath)

sp = simparams.Nico2()


#sp.name = "test"
sp.snc_type = 1000

"""
megalut.sim.run.multi(
	simdir=config.simdir,
	simparams=sp,
	drawcatkwargs={"n":10, "nc":1, "stampsize":config.stampsize},
	drawimgkwargs={}, 
	psfcat=psfcat, psfselect="random",
	ncat=100, nrea=1, ncpu=config.ncpu,
	savepsfimg=False, savetrugalimg=False
	)



megalut.meas.run.onsims(
	simdir=config.simdir,
	simparams=sp,
	measdir=config.simdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":config.stampsize},
	ncpu=config.ncpu,
	skipdone=True
	)

"""
cat = megalut.meas.avg.onsims(
	measdir=config.simdir, 
	simparams=sp,
	task="group",
	groupcols=measfcts.default_groupcols, 
	removecols=measfcts.default_removecols
	)


#megalut.tools.table.keepunique(cat)
megalut.tools.io.writepickle(cat, os.path.join(config.simdir, sp.name, "groupmeascat.pkl"))


cat = megalut.tools.io.readpickle(os.path.join(config.simdir, sp.name, "groupmeascat.pkl"))
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
#print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(config.simdir, sp.name, "groupmeascat_cases.pkl"))









"""
sp.name = "test"
sp.snc_type = 0


megalut.sim.run.multi(
	simdir=config.simdir,
	simparams=sp,
	drawcatkwargs={"n":10000, "nc":100, "stampsize":config.stampsize},
	drawimgkwargs={}, 
	psfcat=psfcat, psfselect="random",
	ncat=1, nrea=1, ncpu=1,
	savepsfimg=False, savetrugalimg=False
	)


"""
"""
megalut.meas.run.onsims(
	simdir=config.simdir,
	simparams=sp,
	measdir=config.simdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":config.stampsize},
	ncpu=1,
	skipdone=False
	)

"""
"""
cat = megalut.meas.avg.onsims(
	measdir=config.simdir, 
	simparams=sp,
	task="group",
	groupcols=measfct.default_groupcols, 
	removecols=measfct.default_removecols
	)

megalut.tools.table.keepunique(cat)
megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat.pkl"))
"""

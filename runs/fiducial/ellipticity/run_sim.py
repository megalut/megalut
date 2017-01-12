import os

import megalut.sim
import megalut.meas
import measfcts
import simparams

import includes

import logging
logger = logging.getLogger(__name__)



psfcat = megalut.tools.io.readpickle(includes.psfcatpath)

# Let's train for ellipticity
# We do not need Shape Noise Cancellation and no shear needeed
sp = simparams.Ellipticity()
sp.shear = 0
sp.snc_type = 1
n = 2500
nc = 20
ncat = 1
nrea = 20


megalut.sim.run.multi(
	simdir=includes.simdir,
	simparams=sp,
	drawcatkwargs={"n":n, "nc":nc, "stampsize":includes.stampsize},
	drawimgkwargs={}, 
	psfcat=psfcat, psfselect="random",
	ncat=ncat, nrea=nrea, ncpu=includes.ncpu,
	savepsfimg=False, savetrugalimg=False
	)



megalut.meas.run.onsims(
	simdir=includes.simdir,
	simparams=sp,
	measdir=includes.simdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":includes.stampsize},
	ncpu=includes.ncpu,
	skipdone=True
	)


cat = megalut.meas.avg.onsims(
	measdir=includes.simdir, 
	simparams=sp,
	task="group",
	groupcols=measfcts.default_groupcols, 
	removecols=measfcts.default_removecols
	)



megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(includes.simdir, sp.name, "groupmeascat.pkl"))

cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_sg", "tru_g", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(includes.simdir, sp.name, "groupmeascat_cases.pkl"))


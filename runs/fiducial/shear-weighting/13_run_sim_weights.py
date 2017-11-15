import os

import megalut.sim
import megalut.meas
import measfcts
import simparams

import includes

import logging
logger = logging.getLogger(__name__)

simdir = includes.simwdir + "large"

# Let's train for ellipticity
# We do not need Shape Noise Cancellation and no shear needeed
sp = simparams.Sersics_statshear()
sp.shear = 0.1
sp.snc_type = 4
sp.noise_level = 0.8
n = 2500
nc = 1
ncat = 500
nrea = 10

megalut.sim.run.multi(
	simdir=simdir,
	simparams=sp,
	drawcatkwargs={"n":n, "nc":nc, "stampsize":includes.stampsize},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=ncat, nrea=nrea, ncpu=includes.ncpu,
	savepsfimg=False, savetrugalimg=False
	)



megalut.meas.run.onsims(
	simdir=simdir,
	simparams=sp,
	measdir=simdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":includes.stampsize},
	ncpu=includes.ncpu,
	skipdone=True
	)

cat = megalut.meas.avg.onsims(
	measdir=simdir, 
	simparams=sp,
	task="group",
	groupcols=measfcts.default_groupcols, 
	removecols=measfcts.default_removecols
	)



megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat.pkl"))

if sp.shear > 0:
	cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
else:
	cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_g1", "tru_g2", "tru_g", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))


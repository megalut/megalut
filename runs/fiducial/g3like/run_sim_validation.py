import os

import megalut.sim
import megalut.meas
import measfcts
import simparams#3D as simparams

import includes

import logging
logger = logging.getLogger(__name__)



# Let's simulate a validation dataset for ellipticity only
# We do not need Shape Noise Cancellation and no shear needeed
sp = simparams.Sersics_statshear()
sp.shear = 0.1
simdir = includes.simvaldir
sp.snc_type = 4
sp.noise_level = 0.8
n = 250
nc = 1
ncat = 300
nrea = 1

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

cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])#["tru_g1", "tru_g2", "tru_g", "tru_flux", "tru_rad"])#"tru_s1", "tru_s2"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))


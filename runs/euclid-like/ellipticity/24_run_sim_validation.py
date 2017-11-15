import os

import megalut.sim
import megalut.meas
from astropy.table import Table
import measfcts
import simparams

import config

import logging
logger = logging.getLogger(__name__)

simdir = config.simvaldir


# Let's simulate a validation dataset for ellipticity only
dbgal = Table.read(os.path.join(config.dbdir, "euclid_test.fits"))
sp = simparams.EuclidLike_Ell(dbgal)
sp.shear = 0.1
sp.snc_type = 1000#0
n = 1
nc = 1
ncat = 250
nrea = 1

psfcat = megalut.tools.io.readpickle(os.path.join(config.psfdir, "psf_meascat.pkl"))
megalut.sim.run.multi(
	simdir=simdir,
	simparams=sp,
	drawcatkwargs={"n":n, "nc":nc, "stampsize":config.stampsize, "pixelscale":config.pixelscale},
	drawimgkwargs={}, 
	psfcat=psfcat, psfselect="random",
	ncat=ncat, nrea=nrea, ncpu=config.ncpu,
	savepsfimg=False, savetrugalimg=False
	)



megalut.meas.run.onsims(
	simdir=simdir,
	simparams=sp,
	measdir=simdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":config.stampsize, "gain":config.gain},
	ncpu=config.ncpu,
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

cat = megalut.tools.io.readpickle(os.path.join(simdir, sp.name, "groupmeascat.pkl"))
cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))
import os

import megalut.sim
import megalut.meas
import megalut.tools as tls
import measfcts
import simparams
import psf

import includes

import logging
logger = logging.getLogger(__name__)

simdir = includes.simvaldir

# Let's train for ellipticity
# We do not need Shape Noise Cancellation and no shear needeed
sp = simparams.EllipticityVarPSF()
# Let's use the same PSF field as for the training
psf_field = tls.io.readpickle(os.path.join(includes.simdir, sp.name, "psf", "psf_field.pkl"))
sp.set_psf_field(psf_field)
sp.shear = 0.1
sp.snc_type = 10000
sp.noise_level = 0.8
n = 1
nc = 1
ncat = 50#2500
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

cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))

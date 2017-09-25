import os

import megalut.sim
import megalut.meas
import measfcts
import simparams

import includes

import logging
logger = logging.getLogger(__name__)

simdir = includes.simdir

# Let's train for ellipticity
# We do not need Shape Noise Cancellation and no shear needeed
sp = simparams.EuclidLike_Ell()
sp.shear = 0
sp.snc_type = 1
sp.noise_factor = 1.
n = 500
nc = 500
ncat = 1
nrea = 10

psfcat = megalut.tools.io.readpickle(os.path.join(includes.psfdir, "psf_meascat.pkl"))

megalut.sim.run.multi(
	simdir=simdir,
	simparams=sp,
	drawcatkwargs={"n":n, "nc":nc, "stampsize":includes.stampsize, "pixelscale":includes.pixelscale},
	drawimgkwargs={}, 
	psfcat=psfcat, psfselect="random",
	ncat=ncat, nrea=nrea, ncpu=includes.ncpu,
	savepsfimg=False, savetrugalimg=True
	)

megalut.meas.run.onsims(
	simdir=simdir,
	simparams=sp,
	measdir=simdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":includes.stampsize, "gain":includes.gain},
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

cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_g2", "tru_g", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))

print cat["snr"]

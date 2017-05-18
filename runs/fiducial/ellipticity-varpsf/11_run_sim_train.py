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

simdir = includes.simdir

# Let's train for ellipticity
# We do not need Shape Noise Cancellation and no shear needeed
sp = simparams.EllipticityVarPSF()
psf_field = psf.PSF_Field(kind="radial")
psfdir = os.path.join(simdir, sp.name, "psf")
psf_field.save(psfdir)
psf_field.plot(psfdir)
sp.set_psf_field(psf_field)
sp.shear = 0
sp.snc_type = 1
sp.noise_level = 0.
n = 10000
nc = 2500
ncat = 1
nrea = 20

megalut.sim.run.multi(
	simdir=simdir,
	simparams=sp,
	drawcatkwargs={"n":n, "nc":nc, "stampsize":includes.stampsize},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=ncat, nrea=nrea, ncpu=includes.ncpu,
	savepsfimg=True, savetrugalimg=False
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

cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_g1", "tru_g2", "tru_g", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))

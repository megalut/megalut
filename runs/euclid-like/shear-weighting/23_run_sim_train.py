import os

import megalut.sim
import megalut.meas
from astropy.table import Table
import measfcts
import simparams

import config

import logging
logger = logging.getLogger(__name__)

simdir = config.simdir

# Let's train for shear
# We do not need Shape Noise Cancellation and no shear needeed
dbgal = Table.read(os.path.join(config.dbdir, "euclid_train_large.fits"))

# nonoise
"""
sp = simparams.EuclidLike_Ell(dbgal)
sp.shear = 0.1
sp.snc_type = 100
sp.noise_factor = 0.
n = 5000
nc = 1
ncat = 4
nrea = 1

"""
# noisy
sp = simparams.EuclidLike_Ell(dbgal)
sp.shear = 0.1
sp.snc_type = 500
sp.noise_factor = 1.
n = 5000
nc = 1
ncat = 2
nrea = 3

"""
# Default
sp = simparams.Default(dbgal)
sp.shear = 0.1
sp.snc_type = 100
sp.noise_factor = 0.
n = 2500
nc = 1
ncat = 1
nrea = 1
"""
"""
# Uniform
sp = simparams.Uniform(dbgal)
sp.shear = 0.1
sp.snc_type = 100
sp.noise_factor = 0.
n = 5000
nc = 1
ncat = 1
nrea = 1
"""

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

if sp.shear > 0:
	cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
else:
	cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_g1", "tru_g2", "tru_g", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))

import os

import megalut.sim
import megalut.meas
from astropy.table import Table
import measfcts
import simparams

import config

import logging
logger = logging.getLogger(__name__)

# Let's train for ellipticity
# We do not need Shape Noise Cancellation and no shear needeed
"""
# UNIFORM
dbgal = Table.read(os.path.join(config.dbdir, "uniform_train.fits"))
sp = simparams.Uniform(dbgal)
sp.shear = 0
sp.snc_type = 1
sp.noise_factor = 0.
n = 20000#0
nc = 2500
ncat = 5
nrea = 3
simdir = os.path.join(config.workdir, "sim")
"""

# Noisy
dbgal = Table.read(os.path.join(config.dbdir, "euclid_train.fits"))
sp = simparams.Uniform(dbgal)
sp.shear = 0
sp.snc_type = 1
n = 100#00#0
nc = 50#0
ncat = 1
nrea = 5#00
simdir = os.path.join(config.workdir, "simnoisy")

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

cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_g2", "tru_g", "tru_flux", "tru_rad"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat_cases.pkl"))



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

"""
# Nico4, to train for ellipticity
# No snc, no shear
sp = simparams.Nico4()
sp.sr = 0
sp.snc_type = 1
n = 2500
nc = 50
ncat = 2
nrea = 100
"""


"""
# Nico4nn, idem but without noise (to see how this does). 5000 cases (too much, but allows for good validation set) and 10 reas.
sp = simparams.Nico4()
sp.name = "Nico4nn"
sp.sr = 0
sp.snc_type = 1
sp.noise_level = 0.0
n = 2500
nc = 50
ncat = 2
nrea = 10 # Even without noise, there is still the position jitter and pixelization
"""


"""
# Nico4shear
# shear, (and snc), for validation. 1000 cases with SNC 10'000
sp = simparams.Nico4()
sp.name = "Nico4shear_snc10000"
sp.sr = 0.1
sp.snc_type = 10000
n = 1
nc = 1
ncat = 500
nrea = 1
"""

"""
sp = simparams.Nico4()
sp.name = "Nico4shear_snc10000_lowSN"
sp.sr = 0.1
sp.snc_type = 10000
sp.lowsn = 1
sp.maxrad = 6
n = 1
nc = 1
ncat = 1000
nrea = 1
"""


# Nico4plotshear
"""
sp = simparams.Nico4()
sp.name = "Nico4plotshear"
sp.sr = 0.0
sp.snc_type = 6
n = 5
nc = 1
ncat = 1
nrea = 1
"""

# Nico4plotellipticity
sp = simparams.Nico4()
sp.name = "Nico4plotell"
sp.sr = 0.0
sp.snc_type = 1000
n = 5
nc = 1
ncat = 4
nrea = 1


megalut.sim.run.multi(
	simdir=config.simdir,
	simparams=sp,
	drawcatkwargs={"n":n, "nc":nc, "stampsize":config.stampsize},
	drawimgkwargs={}, 
	psfcat=psfcat, psfselect="random",
	ncat=ncat, nrea=nrea, ncpu=config.ncpu,
	savepsfimg=False, savetrugalimg=False
	)


megalut.meas.run.onsims(
	simdir=config.simdir,
	simparams=sp,
	measdir=config.simdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":config.stampsize},
	ncpu=config.ncpu,
	skipdone=False
	)



cat = megalut.meas.avg.onsims(
	measdir=config.simdir, 
	simparams=sp,
	task="group",
	groupcols=measfcts.default_groupcols, 
	removecols=measfcts.default_removecols
	)



megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(config.simdir, sp.name, "groupmeascat.pkl"))



# For shear sims, add this
"""
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2", "tru_flux", "tru_rad"])
#cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
megalut.tools.table.keepunique(cat)
print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(config.simdir, sp.name, "groupmeascat_cases.pkl"))
"""





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

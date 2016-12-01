import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import measfcts

ncpu = 10


# This is to get shear-cases with reas that only differ in orientation and noise, for training.

sp = simparams.Simple1()
#sp.name = "Simple1"
#sp.name += "-test"
sp.snc_type = 100

# No shear, just ellipticity:
sp.name = "Simple0"
sp.snc_type = 1
nrea = 100


megalut.sim.run.multi(
	simdir=workdir,
	simparams=sp,
	drawcatkwargs={"n":1000, "nc":50, "stampsize":64},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=1, nrea=50, ncpu=ncpu,
	savepsfimg=False, savetrugalimg=False
	)


megalut.meas.run.onsims(
	simdir=workdir,
	simparams=sp,
	measdir=workdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":64},
	ncpu=ncpu,
	skipdone=True
	)


cat = megalut.meas.avg.onsims(
	measdir=workdir, 
	simparams=sp,
	task="group",
	groupcols=measfcts.default_groupcols, 
	removecols=measfcts.default_removecols
	)

megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat.pkl"))

cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat.pkl"))
#cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_g2"])

megalut.tools.table.keepunique(cat)
#print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))




# This is to get fake obsevations, single realization.
"""

sp = simparams.Simple1()
sp.name += "_obs"

sp.snc_type = 1



megalut.sim.run.multi(
	simdir=workdir,
	simparams=sp,
	drawcatkwargs={"n":10000, "nc":100, "stampsize":128},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=100, nrea=1, ncpu=ncpu,
	savepsfimg=False, savetrugalimg=False
	)

megalut.meas.run.onsims(
	simdir=workdir,
	simparams=sp,
	measdir=workdir,
	measfct=measfct.default,
	measfctkwargs={"stampsize":128},
	ncpu=ncpu,
	skipdone=True
	)


cat = megalut.meas.avg.onsims(
	measdir=workdir, 
	simparams=sp,
	task="group",
	groupcols=measfct.default_groupcols, 
	removecols=measfct.default_removecols
	)

megalut.tools.table.keepunique(cat)
megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat.pkl"))
"""

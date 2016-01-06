import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import measfct

ncpu = 6

"""

# This is to get shear-cases with reas that only differ in orientation and noise, for training.

sp = simparams.GauShear1()

megalut.sim.run.multi(
	simdir=workdir,
	simparams=sp,
	drawcatkwargs={"n":10, "nc":1, "stampsize":128},
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

megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat.pkl"))

cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat.pkl"))
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2", "tru_flux", "tru_sigma"])
megalut.tools.table.keepunique(cat)
#print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))

"""




# This is to get fake obsevations, single realization.


sp = simparams.GauShear2()

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

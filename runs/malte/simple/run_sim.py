import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import measfct
import mlparams

sp = simparams.GauShear1()


"""
megalut.sim.run.multi(
	simdir=workdir,
	simparams=sp,
	drawcatkwargs={"n":10, "nc":1, "stampsize":128},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=100, nrea=1, ncpu=10,
	savepsfimg=False, savetrugalimg=False
	)

megalut.meas.run.onsims(
	simdir=workdir,
	simparams=sp,
	measdir=workdir,
	measfct=measfct.default,
	measfctkwargs={"stampsize":128},
	ncpu=10,
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
"""

"""
cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat.pkl"))
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2", "tru_flux", "tru_sigma"])
megalut.tools.table.keepunique(cat)
megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
"""

"""
cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
print megalut.tools.table.info(cat)
"""

"""
# Training
cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
traindir = os.path.join(workdir, "train_" + sp.name)
megalut.learn.run.train(cat, traindir, mlparams.trainparamslist, ncpu=2)
"""

# Self-predicting

traindir = os.path.join(workdir, "train_" + sp.name)
cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))
cat = megalut.learn.run.predict(cat, traindir, mlparams.trainparamslist)

print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "selfprecat.pkl"))

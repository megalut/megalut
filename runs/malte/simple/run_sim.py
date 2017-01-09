import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import measfcts

ncpu = 10


# This is to get shear-cases with reas that only differ in orientation and noise, for training.

#sp = simparams.Simple1()
#sp.name = "Simple1"
#sp.name += "-test"
#sp.snc_type = 100

# No shear, just ellipticity:
#sp.name = "Simple0"
#sp.snc_type = 1
#sp.sr = 0.0

# idem as 0, but 10 times more realizations
#sp.name = "Simple2"
#sp.snc_type = 1
#sp.sr = 0.0

# Going back to shear : one train set with snc, and a trueley separate validation set without
sp = simparams.Simple1()
sp.name = "SimpleS1"
sp.snc_type = 1000
sp.sr = 0.1
# n 50
# nc 1
# ncat 20
# nrea 1


#sp = simparams.Simple1v()
#sp.name = "SimpleS1v"
#sp.snc_type = 1
#sp.sr = 0.1
# n 10000
# nc 100
# ncat 100
# nrea 1


"""
megalut.sim.run.multi(
	simdir=workdir,
	simparams=sp,
	drawcatkwargs={"n":10000, "nc":100, "stampsize":64},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=100, nrea=1, ncpu=ncpu,
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

"""
cat = megalut.tools.io.readpickle(os.path.join(workdir, sp.name, "groupmeascat.pkl"))
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
#cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_g1", "tru_g2"])

megalut.tools.table.keepunique(cat)
#print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(workdir, sp.name, "groupmeascat_cases.pkl"))





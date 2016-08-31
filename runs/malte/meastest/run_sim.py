import matplotlib
matplotlib.use("AGG")

execfile("config.py")

import simparams
import measfct


ncpu = 1


sp = simparams.GauShear1()

"""
megalut.sim.run.multi(
	simdir=workdir,
	simparams=sp,
	drawcatkwargs={"n":1000, "nc":50, "stampsize":128},
	drawimgkwargs={}, 
	psfcat=None, psfselect="random",
	ncat=1, nrea=1, ncpu=ncpu,
	savepsfimg=False, savetrugalimg=False
	)
"""

megalut.meas.run.onsims(
	simdir=workdir,
	simparams=sp,
	measdir=workdir,
	measfct=measfct.default,
	measfctkwargs={"stampsize":128},
	ncpu=ncpu,
	skipdone=False
	)

"""

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



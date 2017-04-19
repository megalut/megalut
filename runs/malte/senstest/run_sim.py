import matplotlib
matplotlib.use("AGG")

import os
import megalut
import config

import simparams
import measfcts



sp = simparams.SampledBDParams(
	name = "test1",
	snc_type = 0,
	shear=0,
	noise_level=1
)
drawconf = {
	"n":20,
	"nc":10,
	"nrea":1,
	"ncat":1,
	"ncpu":1,
	"groupmode":"g",
	"skipdone":True	
}



psfcat = megalut.tools.io.readpickle(config.psfcatpath)
simdir = config.simdir
measdir = config.simmeasdir
	

# Simulating images
megalut.sim.run.multi(
	simdir=simdir,
	simparams=sp,
	drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize},
	drawimgkwargs={}, 
	psfcat=psfcat, psfselect="random",
	ncat=drawconf["ncat"], nrea=drawconf["nrea"], ncpu=drawconf["ncpu"],
	savepsfimg=False, savetrugalimg=False
)


# Measuring the newly drawn images
megalut.meas.run.onsims(
	simdir=simdir,
	simparams=sp,
	measdir=measdir,
	measfct=measfcts.default,
	measfctkwargs={"stampsize":config.stampsize},
	ncpu=drawconf["ncpu"],
	skipdone=drawconf["skipdone"]
)
	

cat = megalut.meas.avg.onsims(
	measdir=measdir, 
	simparams=sp,
	task="group",
	groupcols=measfcts.default_groupcols, 
	removecols=measfcts.default_removecols
)


megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat.pkl"))


cat = megalut.tools.io.readpickle(os.path.join(simdir, sp.name, "groupmeascat.pkl"))
cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])


megalut.tools.table.keepunique(cat)
#print megalut.tools.table.info(cat)
megalut.tools.io.writepickle(cat, os.path.join(simdir, sp.name, "groupmeascat.pkl"))




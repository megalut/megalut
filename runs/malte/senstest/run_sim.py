import matplotlib
matplotlib.use("AGG")

import os
import megalut
import config

import simparams
import measfcts


####################


"""
# Comparing to the observations:
sp = simparams.SampledBDParams(
	name = "simobscompa",
	snc_type = 0,
	shear = 0,
	noise_level = 10.0, #5.4
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":100,
	"nc":10,
	"nrea":1,
	"ncat":10,
	"ncpu":10,
	"groupmode":None,
	"skipdone":True	
}
"""
"""
# Validation: 100 different shear cases 
sp = simparams.SampledBDParams_statshear(
	name = "val1",
	snc_type = 2,
	shear = 0.06,
	noise_level = 10.0, #5.4
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":200,
	"nc":10,
	"nrea":1,
	"ncat":100,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":True	
}
"""

# Shear training:
sp = simparams.SampledBDParams_statshear(
	name = "st-ln-1",
	snc_type = 10,
	shear = 0.1,
	noise_level = 1.0, # WARNING, REDUCED NOISE
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":100,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":True	
}


####################



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

megalut.tools.table.keepunique(cat)
megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))


if drawconf["groupmode"] == "shear":

	cat = megalut.tools.io.readpickle(os.path.join(measdir, sp.name, "groupmeascat.pkl"))
	cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])

	megalut.tools.table.keepunique(cat)
	#print megalut.tools.table.info(cat)
	megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))




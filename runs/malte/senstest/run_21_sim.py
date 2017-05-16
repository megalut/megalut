import matplotlib
matplotlib.use("AGG")

import os
import megalut
import config

import simparams
import measfcts
import numpy as np

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)



####################


"""
# Comparing to the observations:
sp = simparams.SampledBDParams(
	name = "simobscompa",
	snc_type = 0,
	shear = 0,
	noise_level = 1.0, # Note: this is relative, in sigma !
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":100,
	"nc":10,
	"nrea":1,
	"ncat":10,
	"ncpu":10,
	"groupmode":None,
	"skipdone":False	
}
"""
"""
# Validation: 200 different shear cases, with 1000 x 4 SNC reas
sp = simparams.SampledBDParams_statshear(
	name = "val-1",
	snc_type = 4,
	shear = 0.06,
	noise_level = 1.0, # Note: this is relative, in sigma !
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":1000,
	"nc":100,
	"nrea":1,
	"ncat":200,
	"ncpu":25,
	"groupmode":"shear",
	"skipdone":False	
}

"""

# Shear training:
"""
sp = simparams.SampledBDParams_statshear(
	name = "ts-ln-1",
	snc_type = 100,
	shear = 0.1,
	noise_level = 0.1, # WARNING REDUCED # Note: this is relative, in sigma !
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":500,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":False	
}
"""
"""
sp = simparams.SampledBDParams_statshear(
	name = "ts-ln-1-large",
	snc_type = 400,
	shear = 0.1,
	noise_level = 0.1, # WARNING REDUCED # Note: this is relative, in sigma !
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":1000,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":False	
}

"""

"""
sp = simparams.SampledBDParams_statshear(
	name = "ts-fn-1",
	snc_type = 1000,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":1000,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":False	
}
"""

"""
# Shear validation:
sp = simparams.SampledBDParams_statshear(
	name = "vs-1",
	snc_type = 1000,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":500,
	"ncpu":25,
	"groupmode":"shear",
	"skipdone":False	
}
"""

"""
# Weight training: BAD: HAS SNC !
sp = simparams.SampledBDParams_statshear(
	name = "tw-1",
	snc_type = 2,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":1000,
	"nc":50,
	"nrea":1,
	"ncat":500,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":False	
}
"""

"""
sp = simparams.SampledBDParams_statshear(
	name = "tw-1-minmag22",
	snc_type = 2,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
	minmag = 22.0,
)
drawconf = {
	"n":1000,
	"nc":50,
	"nrea":1,
	"ncat":500,
	"ncpu":10,
	"groupmode":"shear",
	"skipdone":False	
}

"""
"""
# Weight training: NOW DONE WITHOUT SNC
sp = simparams.SampledBDParams_statshear(
	name = "tw-2-nsnc",
	snc_type = 0,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":2000,
	"nc":50,
	"nrea":1,
	"ncat":500,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":False	
}
"""
"""
sp = simparams.SampledBDParams_statshear(
	name = "tw-2-nsnc-small",
	snc_type = 0,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":200,
	"nc":50,
	"nrea":1,
	"ncat":500,
	"ncpu":10,
	"groupmode":"shear",
	"skipdone":False	
}
"""
sp = simparams.SampledBDParams_statshear(
	name = "tw-2-nsnc-bigrea",
	snc_type = 0,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
)
drawconf = {
	"n":100000,
	"nc":100,
	"nrea":1,
	"ncat":20,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":False	
}



"""
sp = simparams.SampledBDParams(
	name = "tw-1-sheargroup4", # So here we use the sheargroup option, to get 4 galaxies per group
	snc_type = 2,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
	sheargroup = 4, # This gives ncat * n/sheargroup cases of different shear, with snc * sheargroup realizations per case. Here (10'000, 8)
	nshearvals = 11000, # Make this larger than the number of cases above.
)
drawconf = {
	"n":2000,
	"nc":20,
	"nrea":1,
	"ncat":20,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":True	
}
"""
"""
sp = simparams.SampledBDParams(
	name = "tw-1-sheargroup4-large", # So here we use the sheargroup option, to get 4 galaxies per group
	snc_type = 2,
	shear = 0.1,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
	sheargroup = 4, # This gives ncat * n/sheargroup cases of different shear, with snc * sheargroup realizations per case. Here (100'000, 8)
	nshearvals = 110000, # Make this larger than the number of cases above.
)
drawconf = {
	"n":2000,
	"nc":20,
	"nrea":1,
	"ncat":200,
	"ncpu":20,
	"groupmode":"shear",
	"skipdone":True	
}
"""



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
	#cat = megalut.tools.table.groupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])
	cat = megalut.tools.table.fastgroupreshape(cat, groupcolnames=["tru_s1", "tru_s2"])

	megalut.tools.table.keepunique(cat)
	
	# For each case, we add the fraction of failed measurements
	nrea = cat["adamom_g1"].shape[1]
	logger.info("We have {} realizations".format(nrea))
	cat["adamom_failfrac"] = np.sum(cat["adamom_g1"].mask, axis=1) / float(nrea)

	#print megalut.tools.table.info(cat)
	megalut.tools.io.writepickle(cat, os.path.join(measdir, sp.name, "groupmeascat.pkl"))




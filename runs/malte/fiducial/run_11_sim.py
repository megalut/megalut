import matplotlib
matplotlib.use("AGG")

import os
import megalut
import config
import argparse

import simparams
import measfcts
import numpy as np

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def define_parser():
	"""Defines the command line arguments
	"""
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('code', type=str, help='what dataset should be simulated?')
	
	return parser


def configure(args):
	"""Configures settings for the different datasets
	"""
	
	code = args.code
	
	if code == "si-1": # Just to quickly draw 1000 galaxies probing the distributions.
		sp = simparams.Fiducial(
			name = code,
			snc_type = 0,
			shear = 0,
			noise_level = 1.0
		)
		drawconf = {
			"n":1000,
			"nc":10,
			"nrea":1,
			"ncat":1,
			"ncpu":1,
			"groupmode":None,
			"skipdone":False	
		}
	
	elif code == "vo-1": # As a first test, no SNC: 100 cases with 10'000 gals (1 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":100,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}

	elif code == "vo-2": # With 2-fold SNC, 1000 cases, 10'000 gals (20 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":10000,
			"nc":100,
			"nrea":1,
			"ncat":1000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	elif code == "ts-1": # 500 cases, 500-SNC rotations per case (tiny...)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 500,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":500,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}


	elif code == "ts-2": # 2000 cases, 2000-SNC rotations per case (4 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 2000,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":2000,
			"ncpu":20,
			"groupmode":"shear",
			"skipdone":False	
		}



	elif code == "vs-1": # Same settings as ts-1, just another realization of the set.
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 500,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":500,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	
	elif code == "vs-2": # 1000 cases, 10'000 SNC rotations each (10 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0
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
	
	elif code == "vs-3": # 5000 cases, 10'000 SNC rotations each (50 M) HUGE, same as Thibault's set.
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 10000,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":1,
			"nc":1,
			"nrea":1,
			"ncat":5000,
			"ncpu":50,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	
	elif code == "tw-1": # Training weights, no SNC (!), 500 cases, 2000 gals (1 M)
		sp = simparams.Fiducial_statshear(
			name = code,
			snc_type = 0,
			shear = 0.1,
			noise_level = 1.0
		)
		drawconf = {
			"n":2000,
			"nc":50,
			"nrea":1,
			"ncat":500,
			"ncpu":10,
			"groupmode":"shear",
			"skipdone":False	
		}
	
	else:
		
		logger.info("Unknown code")
		return
		
	
	return (sp, drawconf)





"""

sp = simparams.Fiducial_statshear(
	name = "ts-1",
	snc_type = 500,
	shear = 0.1,
	noise_level = 1.0
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":500,
	"ncpu":10,
	"groupmode":"shear",
	"skipdone":False	
}
"""




#################### What we really need

"""
# 900 cases, 400 realizations
sp = simparams.SampledBDParams_statshear(
	name = "ts-ln-1-large",
	snc_type = 400,
	shear = 0.1,
	noise_level = 0.1, # WARNING REDUCED # Note: this is relative, in sigma !
	ecode = config.ecode,
	scode = config.scode,
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":900,
	"ncpu":30,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""


"""
# 30 cases, 50000 reas without SNC
sp = simparams.SampledBDParams_statshear(
	name = "tw-2-nsnc-bigrea",
	snc_type = 0,
	shear = 0.1,
	noise_level = 1.0,
	ecode = config.ecode,
	scode = config.scode,

)
drawconf = {
	"n":50000,
	"nc":100,
	"nrea":1,
	"ncat":30,
	"ncpu":30,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""
"""
# 900 cases, 1000 reas without SNC
sp = simparams.SampledBDParams_statshear(
	name = "tw-3-nsnc",
	snc_type = 0,
	shear = 0.07,
	noise_level = 1.0,
	ecode = config.ecode,
	scode = config.scode,

)
drawconf = {
	"n":1000,
	"nc":10,
	"nrea":1,
	"ncat":900,
	"ncpu":30,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""

"""
sp = simparams.SampledBDParams(
	name = "vo-mimicdata", # 12800 cases of shear with 4 x 2 reas per case
	snc_type = 2,
	shear = 0.07,
	noise_level = 1.0,
	ecode = config.ecode,
	scode = config.scode,
	sheargroup = 4, # This gives ncat * n/sheargroup cases of different shear, with snc * sheargroup realizations per case. Here (12800, 8)
	nshearvals = 110000, # Make this larger than the number of cases above.
)
drawconf = {
	"n":5120,
	"nc":10,
	"nrea":1,
	"ncat":10,
	"ncpu":10,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""
"""
sp = simparams.SampledBDParams(
	name = "vo-mimicdata-dbshear", # 12800 cases of shear with 4 x 2 reas per case
	snc_type = 2,
	shear = 20.0, # >10, so we will take it from the db
	noise_level = 1.0,
	ecode = config.ecode,
	scode = config.scode,
	sheargroup = 4, # This gives ncat * n/sheargroup cases of different shear, with snc * sheargroup realizations per case. Here (12800, 8)
	nshearvals = 110000, # Make this larger than the number of cases above.
)
drawconf = {
	"n":5120,
	"nc":10,
	"nrea":1,
	"ncat":10,
	"ncpu":10,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""




"""
sp = simparams.SampledBDParams(
	name = "vo-mimicdata-6", # 6*12800 cases of shear with 4 x 2 reas per case
	snc_type = 2,
	shear = 0.05,
	noise_level = 1.0,
	ecode = config.ecode,
	scode = config.scode,
	sheargroup = 4, # This gives ncat * n/sheargroup cases of different shear, with snc * sheargroup realizations per case. Here (6*12800, 8)
	nshearvals = 110000, # Make this larger than the number of cases above.
)
drawconf = {
	"n":5120,
	"nc":10,
	"nrea":1,
	"ncat":60,
	"ncpu":30,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""




######## Special exploration
"""
# 900 cases, 1000 realizations, half noise !
sp = simparams.SampledBDParams_statshear(
	name = "ts-hn-1-large",
	snc_type = 1000,
	shear = 0.1,
	noise_level = 0.5, # WARNING REDUCED # Note: this is relative, in sigma !
	ecode = config.ecode,
	scode = config.scode,
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":900,
	"ncpu":30,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""

"""
# 900 cases, 1000 realizations, full noise !
sp = simparams.SampledBDParams_statshear(
	name = "vs-1-large",
	snc_type = 1000,
	shear = 0.1,
	noise_level = 1.0,
	ecode = config.ecode,
	scode = config.scode,
)
drawconf = {
	"n":1,
	"nc":1,
	"nrea":1,
	"ncat":900,
	"ncpu":30,
	"groupmode":"shear",
	"skipdone":False,
	"psfcatpath":config.psfcatpath,
}
"""




#################### Experiments on fiducial set
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
"""
sp = simparams.SampledBDParams(
	name = "vo-mimicdata", # 12800 cases of shear with 4 x 2 reas per case
	snc_type = 2,
	shear = 0.05,
	noise_level = 1.0,
	ecode = "ep0", # others are em2
	sheargroup = 4, # This gives ncat * n/sheargroup cases of different shear, with snc * sheargroup realizations per case. Here (12800, 8)
	nshearvals = 110000, # Make this larger than the number of cases above.
)
drawconf = {
	"n":5120,
	"nc":10,
	"nrea":1,
	"ncat":10,
	"ncpu":10,
	"groupmode":"shear",
	"skipdone":True	
}
"""



def run(configuration):
	"""Draws the simulations and measures them
	"""
	sp, drawconf = configuration
	
	simdir = config.simdir
	measdir = config.simmeasdir


	# Simulating images
	megalut.sim.run.multi(
		simdir=simdir,
		simparams=sp,
		drawcatkwargs={"n":drawconf["n"], "nc":drawconf["nc"], "stampsize":config.drawstampsize},
		drawimgkwargs={}, 
		psfcat=None, psfselect="random",
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


if __name__ == '__main__':
	parser = define_parser()
	args = parser.parse_args()
	status = run(configure(args))
	exit(status)

